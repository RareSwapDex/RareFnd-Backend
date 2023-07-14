from django.contrib import admin
from RareFndApp.models import (
    User,
    Category,
    Subcategory,
    Project,
    Type,
    Country,
    Contribution,
    Release,
    PendingContribution,
    TokenPrice,
    Incentive,
    RareFndData,
    ProjectFile,
    EligibleCountry,
)
import traceback
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from RareFndApp.models import User
from django.contrib import messages
from django.core.mail import BadHeaderError
from .tasks import backend_send_html_email
import threading
import queue


def backend_send_html_email_with_exception_handling(
    subject, message, email_from, recipient_list, exception_queue
):
    try:
        backend_send_html_email(subject, message, email_from, recipient_list)
    except Exception as e:
        exception_queue.put((traceback.format_exc(), str(e)))


def send_emails_to_subscribed_users(modeladmin, request, queryset):
    if queryset.count() > 3:  # or any number that suits your needs
        modeladmin.message_user(
            request,
            "Cannot send emails to more than 3 projects at once.",
            messages.ERROR,
        )
        return

    email_from = settings.EMAIL_HOST_USER
    for project in queryset:
        project_url = (
            f"https://rarefnd.com/projects/{project.owner.username}/"
            + project.title.replace(" ", "-")
        )
        subscribers_subject = f"{project.title} is now live!"
        subscribers_message = f"""
            <html>
            <body>
                <p>We're excited to let you know that the project "<b>{project.title}</b>" you've subscribed to is now live on our platform!</p>

                <p>Now is the time to take action! You can show your support and help the project reach its goal by contributing. Remember, every contribution, no matter how big or small, can make a difference.</p>

                <p>You can view the project and make your contribution here:</p>
                <a href="{project_url}">{project.title}</a>

                <p>Thank you for being a part of our community!</p>

                <p>Best Regards,</p>
                <p>The Rare Find Team</p>
            </body>
            </html>
            """
        owner_subject = f"Congratulations, {project.title} is now live!"
        owner_message = f"""
            <html>
            <body>
                <p>We're thrilled to let you know that your project "<b>{project.title}</b>" is now live on our platform!</p>

                <p>Now is the time to take action! You can show your support and help the project reach its goal by contributing. Remember, every contribution, no matter how big or small, can make a difference.</p>

                <p>You can view your project here:</p>
                <a href="{project_url}">{project.title}</a>

                <p>If you have any questions or need assistance in promoting your project, please do not hesitate to reach out to us.</p>

                <p>Thank you for choosing our platform for your project! We're excited to see it succeed.</p>

                <p>Best Regards,</p>
                <p>The Rare Find Team</p>
            </body>
            </html>
            """
        subscribers_recipient_list = [
            user.email for user in project.subscribed_users.all()
        ]
        # send emails to subscribers
        exception_queue = queue.Queue()
        thread = threading.Thread(
            target=backend_send_html_email_with_exception_handling,
            args=(
                subscribers_subject,
                subscribers_message,
                email_from,
                subscribers_recipient_list,
                exception_queue,
            ),
        )
        thread.start()
        thread.join()  # wait for the thread to finish

        if not exception_queue.empty():
            exception_traceback, exception_message = exception_queue.get()
            print(exception_traceback)
            modeladmin.message_user(
                request,
                f'Error sending emails to subscribers of "{project.title}": {exception_message}',
                messages.ERROR,
            )
        else:
            modeladmin.message_user(
                request,
                f'Emails were successfully sent to subscribers of "{project.title}".',
                messages.SUCCESS,
            )
        # send email to owner
        exception_queue = queue.Queue()
        thread = threading.Thread(
            target=backend_send_html_email_with_exception_handling,
            args=(
                owner_subject,
                owner_message,
                email_from,
                [project.owner.email],
                exception_queue,
            ),
        )
        thread.start()
        thread.join()  # wait for the thread to finish

        if not exception_queue.empty():
            exception_traceback, exception_message = exception_queue.get()
            print(exception_traceback)
            modeladmin.message_user(
                request,
                f'Error sending email "{project.owner.email}" owner of project "{project.title}": {exception_message}',
                messages.ERROR,
            )
        else:
            modeladmin.message_user(
                request,
                f'Email was successfully sent to "{project.owner.email}" owner of project "{project.title}".',
                messages.SUCCESS,
            )


send_emails_to_subscribed_users.short_description = (
    "Send emails to owner and subscribed users"
)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "wallet_address",
            "total_contributions",
        )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField(
        label=("Password"),
        help_text=(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="../password/">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "phone",
            "wallet_address",
            "total_contributions",
            "is_active",
            "is_admin",
        )


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "phone",
        "wallet_address",
        "total_contributions",
        "is_admin",
    )
    list_filter = ("is_admin", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "profile_picture",
                    "bio",
                    "phone",
                    "wallet_address",
                    "total_contributions",
                    "is_active",
                )
            },
        ),
        ("Permissions", {"fields": ("is_admin",)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "phone",
                    "wallet_address",
                    "total_contributions",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


class ProjectAdmin(admin.ModelAdmin):
    actions = [send_emails_to_subscribed_users]


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Release)
admin.site.register(Contribution)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Type)
admin.site.register(Country)
admin.site.register(PendingContribution)
admin.site.register(TokenPrice)
admin.site.register(Incentive)
admin.site.register(RareFndData)
admin.site.register(ProjectFile)
admin.site.register(EligibleCountry)
admin.site.register(Project, ProjectAdmin)

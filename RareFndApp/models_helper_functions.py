from .models import (
    Project,
    Category,
    Contribution,
    PendingContribution,
    TokenPrice,
    User,
    Incentive,
    Subcategory,
    Country,
    RareFndData,
    ProjectFile,
    Type,
    EligibleCountry,
)
import random
import string
from django.core.mail import EmailMessage
from django.conf import settings


def backend_send_html_email(subject, message, email_from, recipient_list):
    email = EmailMessage(
        subject,
        message,
        email_from,
        recipient_list,
    )
    email.content_subtype = "html"
    email.send()


def add_amount_to_project_raised_amount(project_id, amount):
    project = Project.objects.get(pk=project_id)
    project_raised_amount = getattr(project, "raised_amount")
    Project.objects.filter(pk=project_id).update(
        raised_amount=project_raised_amount + amount
    )


def check_project_reached_target(project_id):
    project = Project.objects.get(pk=project_id)
    project_fund_amount = getattr(project, "fund_amount")
    project_raised_amount = getattr(project, "raised_amount")
    project_current_reward = getattr(project, "current_reward")
    if (project_raised_amount + project_current_reward) >= project_fund_amount:
        Project.objects.filter(pk=project_id).update(live=False)


def add_contribution_to_contribution_table(
    contributor_wallet_address,
    contributor_email,
    project_id,
    contribution_amount,
    contribution_method,
    contribution_hash,
    selected_incentive,
):
    project = Project.objects.get(pk=project_id)
    selected_incentive = False if selected_incentive == "False" else selected_incentive
    incentive_obj = (
        Incentive.objects.get(pk=int(selected_incentive))
        if selected_incentive
        else None
    )
    c = Contribution(
        contributor_wallet_address=contributor_wallet_address,
        contributor_email=contributor_email,
        project=project,
        amount=contribution_amount,
        contribution_method=contribution_method,
        hash="random_"
        + "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(12)
        ),
        selected_incentive=Incentive.objects.get(pk=int(selected_incentive))
        if selected_incentive
        and Incentive.objects.get(pk=int(selected_incentive)).price > 0
        else None,
        eligible_for_selected_incentive=contribution_amount >= incentive_obj.price
        if selected_incentive
        and Incentive.objects.get(pk=int(selected_incentive)).price > 0
        else False,
    )
    if (
        selected_incentive
        and contribution_amount >= incentive_obj.price
        and Incentive.objects.get(pk=int(selected_incentive)).price > 0
    ):
        Incentive.objects.filter(id=int(selected_incentive)).update(
            available_items=incentive_obj.available_items - 1,
            reserved=incentive_obj.reserved + 1,
        )
    c.clean()
    c.save()

    return (
        incentive_obj.title
        if selected_incentive
        and contribution_amount >= incentive_obj.price
        and Incentive.objects.get(pk=int(selected_incentive)).price > 0
        else False
    )


def send_contribution_email(recipient_list, reward, project_id):
    # Retrieve the project title using the project_id
    project = Project.objects.get(pk=project_id)
    project_title = project.title

    # Construct the reward message if it's not False
    if reward:
        reward_message = f"<p>As a token of appreciation, you'll be receiving the reward: <strong>{reward}</strong>.</p>"
    else:
        reward_message = ""

    email_message = f"""
    <html>
    <body>
    <p>Dear Contributor,</p>

    <p>Thank you so much for your generous contribution to the project, <strong>{project_title}</strong>. Your contribution of <strong>{contribution_amount}</strong> is greatly appreciated and will go a long way in helping us achieve our goals.</p>

    {reward_message}

    <p>Your support means everything to us. We're excited to have you on board and will keep you updated on our progress. Together, we'll make this project a huge success!</p>

    <p>Warm regards,<br>RareFND Team</p>
    </body>
    </html>
    """

    backend_send_html_email(
        subject="Thank You for Your Contribution to RareFND!",
        message=email_message,
        email_from=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
    )

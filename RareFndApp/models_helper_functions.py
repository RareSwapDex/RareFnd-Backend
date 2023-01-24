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
    MercuryoPendingStake,
)


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
    c = Contribution(
        contributor_wallet_address=contributor_wallet_address,
        contributor_email=contributor_email,
        project=project,
        amount=contribution_amount,
        contribution_method=contribution_method,
        hash=contribution_hash,
        selected_incentive=Incentive.objects.get(pk=int(selected_incentive)),
        eligible_for_selected_incentive=contribution_amount
        >= Incentive.objects.get(pk=int(selected_incentive)).price,
    )
    c.clean()
    c.save()

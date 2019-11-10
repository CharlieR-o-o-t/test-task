# Bootstrap the Sentry environment
from sentry.utils.runner import configure
configure()

from os import environ

# Do something crazy
from sentry.models import (
    Team, Project, ProjectKey, User, Organization, OrganizationMember,
    OrganizationMemberTeam
)

organization = Organization()
organization.name = environ.get('SENTRY_ORG_NAME', 'DefaultOrg') 
organization.save()

team = Team()
team.name = environ.get('SENTRY_TEAM_NAME', 'Sentry') 
team.organization = organization
team.save()

project = Project()
project.team = team
project.add_team(team)
project.name = 'Default'
project.organization = organization
project.save()

user = User()
user.username = environ.get('SENTRY_ADMIN_NAME', 'admin') 
user.email = environ.get('SENTRY_ADMIN_EMAIL', 'admin@localhost') 
user.is_superuser = True
user.set_password(environ.get('SENTRY_ADMIN_PASSWORD', 'admin'))
user.save()

member = OrganizationMember.objects.create(
    organization=organization,
    user=user,
    role='owner',
)

OrganizationMemberTeam.objects.create(
    organizationmember=member,
    team=team,
)

key = ProjectKey.objects.filter(project=project)[0]
print 'SENTRY_DSN = "%s"' % (key.get_dsn(),)

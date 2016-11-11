"""upr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from upr import views
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
	url(r'^v1/upr/users/$',views.UserCreateView.as_view(), name= 'User List'),
	url(r'^v1/upr/users/auth/$',views.UserAuthView.as_view(), name= 'User auth'),
	url(r'^v1/upr/users/AG/$',views.AGView.as_view(), name= 'Create Application Graph'),
	url(r'^v1/upr/users/RAG/$',views.RAGView.as_view(), name= 'Create Reconciled Application Graph'),
	url(r'^v1/upr/users/SG/$',views.SGView.as_view(), name= 'Create Service Graph'),

	url(r'^v1/upr/users/(?P<user_id>[^/]+)/$',views.UserView.as_view(), name= 'User'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/UserType/$',views.UserTypeView.as_view(), name= 'User Type'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/Creator/$',views.UserCreatorView.as_view(), name= 'User Creator'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/CreatedUsers/$',views.CreatedUsersView.as_view(), name= 'Users Created'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/PSA/$',views.UserPSAView.as_view(), name= 'User PSA'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/Groups/$',views.UserGroupView.as_view(), name= 'User Group'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/HSPL/$',views.UserHSPLView.as_view(), name= 'User HSPL'),
	#url(r'^v1/upr/users/(?P<user_id>[^/]+)/HSPL/executed/$',views.UserHSPLExView.as_view(), name= 'User HSPL Executed'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/OptProfile/$',views.OptProfileView.as_view(), name= 'OptProfile'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/AG/$',views.UserAGView.as_view(), name= 'Application Graph'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/RAG/$',views.UserRAGView.as_view(), name= 'Reconciled Application Graph'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/PSAConf/$',views.UserLowLevelView.as_view(), name= 'Low Level Configuration'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/ExecutePSA/$',views.ExecutePSAView.as_view(), name= 'Execute PSA'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/reconciliation_report/$',views.ReconciliationReportView.as_view(), name= 'Reconciliation Report'),
	url(r'^v1/upr/groups/$',views.GroupListView.as_view(), name= 'Group List'),
	url(r'^v1/upr/groups/(?P<group_id>[^/]+)/$',views.GroupView.as_view(), name= 'Group'),
	url(r'^v1/upr/groups/(?P<group_id>[^/]+)/users/$',views.GroupUserView.as_view(), name= 'Group Users'),
	url(r'^v1/upr/groups/(?P<group_id>[^/]+)/PSA/$',views.GroupPSAView.as_view(), name= 'Group PSA'),
	url(r'^v1/upr/MSPL/$',views.MSPLView.as_view(), name= 'MSPL'),
	url(r'^v1/upr/HSPL/$',views.HSPLView.as_view(), name= 'HSPL'),	
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/MSPL/$',views.UserMSPLPSAView.as_view(), name= 'User MSPL PSA'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/sfa_report/$',views.SFAView.as_view(), name= 'Create SFA_report'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/ifa_report/$',views.UserIFAView.as_view(), name= 'User IFA_report'),
	url(r'^v1/upr/users/(?P<user_id>[^/]+)/mifa_report/$',views.UserMIFAView.as_view(), name= 'User MIFA_report'),

	url(r'^v1/upr/users/(?P<user_id>[^/]+)/SG/$',views.UserSGView.as_view(), name= 'Service Graph'),


	url(r'^docs/', include('rest_framework_swagger.urls')),	 	


]

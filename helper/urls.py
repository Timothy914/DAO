from django.urls import path
from .views import DProject, user, schedule, group


app_name = 'helper'
urlpatterns = [
    path('register/', user.register, name='register'),
    path('login/', user.login, name='login'),
    path('', user.index, name='index'),
    path('user/home/', user.home, name='home'),
    path('user/pwd_change/', user.pwd_change, name='pwd_change'),
    path('user/friends_admin/', user.friends_admin, name='friends_admin'),
    path('dproject/home/', DProject.home, name='dproject_homepage'),
    path('dproject/hot/<int:pg>', DProject.hot, name='hot'),
    path('dproject/<int:pk>/modify', DProject.modify, name='dproject_modify'),
    path('dproject/<int:pk>/delete', DProject.delete, name='dproject_delete'),
    path('dproject/add', DProject.add, name='dproject_add'),
    path('dproject/<int:pk>/', DProject.dproject, name='dproject_page'),
    path('dproject/friend/<int:friend_id>/', DProject.public, name='public'),
    path('logout/', user.logout, name='logout'),
    path('group/<int:pid>/', group.group_admin, name='group_admin'),
    path('group/<int:pid>/<int:pk>/', group.home, name='group_home'),
    path('group/<int:pid>/<int:pk>/add_assign/', group.add_assign, name='assign_add'),
    path('group/<int:pid>/<int:pk>/add_sub_assign/', group.add_sub_assign, name='sub_assign_add'),
    path('schedule/', schedule.home, name='schedule_home'),
    path('schedule/add/', schedule.add_todo_list, name='schedule_add'),
    path('schedule/daily', schedule.daily_schedules, name='schedule_daily'),
]

from django.urls import path

from .views import *

urlpatterns = [
    path('', PostsListView.as_view(), name='posts_list'),
    path('post_create/', PostCreateView.as_view(), name='post_create'),
    path('post_detail/<int:pk>', PostDetailView.as_view(), name='post_detail'),
    path('post_delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
    path('post_create/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    path('categories/', CategoryList.as_view(), name='categories_list'),
    path('add_subscriber/<int:pk>', add_subscriber, name='add_subscriber'),
    path('remove_subscriber/<int:pk>', remove_subscriber, name='remove_subscriber'),
    path('category_detail/<int:pk>', CategoryDetail.as_view(), name='category_detail'),
]

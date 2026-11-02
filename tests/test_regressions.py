"""Дополнительные проверки изоляции данных и контракта API."""

import pytest
from django.db import IntegrityError, transaction

from posts.models import Follow


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('method', ('get', 'put', 'patch', 'delete'))
def test_comment_cannot_be_accessed_through_other_post(
    user_client, post, another_post, comment_1_post, method,
):
    url = (f'/api/v1/posts/{another_post.pk}/comments/'
           f'{comment_1_post.pk}/')
    assert getattr(user_client, method)(url).status_code == 404
    comment_1_post.refresh_from_db()
    assert comment_1_post.post == post


@pytest.mark.parametrize('method', ('get', 'post'))
def test_missing_parent_post_returns_404(user_client, method):
    response = getattr(user_client, method)(
        '/api/v1/posts/99999/comments/', {'text': 'New comment'},
    )
    assert response.status_code == 404


def test_post_author_cannot_be_spoofed(user_client, user, another_user):
    response = user_client.post('/api/v1/posts/', {
        'text': 'New post', 'author': another_user.username,
    })
    assert response.status_code == 201
    assert response.json()['author'] == user.username


def test_follow_owner_cannot_be_spoofed(user_client, user, another_user):
    response = user_client.post('/api/v1/follow/', {
        'user': another_user.username, 'following': another_user.username,
    })
    assert response.status_code == 201
    assert Follow.objects.get().user == user


def test_follow_unique_constraint(user, another_user):
    Follow.objects.create(user=user, following=another_user)
    with pytest.raises(IntegrityError), transaction.atomic():
        Follow.objects.create(user=user, following=another_user)


@pytest.mark.parametrize('method', ('put', 'patch', 'delete'))
def test_follow_list_disallows_other_operations(user_client, method):
    assert getattr(user_client, method)('/api/v1/follow/').status_code == 405


def test_empty_post_list_is_paginated_when_limit_is_supplied(client):
    response = client.get('/api/v1/posts/?limit=2')
    assert response.status_code == 200
    assert response.json() == {
        'count': 0, 'next': None, 'previous': None, 'results': [],
    }

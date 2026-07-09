import pytest
from tests.factories import UserFactory


@pytest.mark.django_db
class TestCustomUserCreationForm:
    def test_valid_form(self):
        from users.forms import CustomUserCreationForm
        form = CustomUserCreationForm(data={
            "username": "newuser",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        assert form.is_valid()

    def test_passwords_dont_match(self):
        from users.forms import CustomUserCreationForm
        form = CustomUserCreationForm(data={
            "username": "newuser",
            "password1": "StrongPass123!",
            "password2": "DifferentPass123!",
        })
        assert not form.is_valid()
        assert "password2" in form.errors

@pytest.mark.django_db
class TestUserProfileForm:
    def test_valid_profile_form(self):
        from users.forms import UserProfileForm
        user = UserFactory()
        form = UserProfileForm(data={
            "username": user.username,
            "email": "new@example.com",
            "phone": "+380991234567",
        }, instance=user)
        assert form.is_valid()

from api.v1.schemes_base import UserProfileBase


class ProfileResponse(UserProfileBase):

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "gender": "MALE",
                "role": "user",
                "email": "john.doe@example.com",
                "is_fictional_email": False,
                "is_email_notify_allowed": True,
                "is_verification_email": True,
                "user_timezone": "America/New_York",
                "date_create_account": "2023-01-15T14:30:00Z",
            }
        }

from models.users import ChangePasswordRequest, LoginRequest, RegisterRequest
from utils.data_generator import DataGenerator


class UserData:
    @staticmethod
    def registration_data(invite_code: str | None = None) -> RegisterRequest:
        return RegisterRequest(
            email=DataGenerator.generate_email(),
            password=DataGenerator.generate_password(),
            full_name=DataGenerator.generate_full_name(),
            invite_code=invite_code,
        )

    @staticmethod
    def login_data(registration: RegisterRequest) -> LoginRequest:
        return LoginRequest(
            email=registration.email,
            password=registration.password,
        )

    @staticmethod
    def update_profile_data() -> dict:
        return {"full_name": DataGenerator.generate_full_name()}

    @staticmethod
    def change_password_data(
        registration: RegisterRequest, new_password
    ) -> ChangePasswordRequest:
        return ChangePasswordRequest(
            old_password=registration.password,
            new_password=new_password,
        )

from sourcing.config import EB_APPLICATION_ID, EB_PRIVATE_KEY_FILE_PATH
from sourcing.enable_banking.client import EnableBankingClient

client = EnableBankingClient(
    private_key_file_path=EB_PRIVATE_KEY_FILE_PATH, application_id=EB_APPLICATION_ID
)

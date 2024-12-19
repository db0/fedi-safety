from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

class Config:
    object_storage_endpoint: str = env.str("OBJECT_STORAGE_ENDPOINT")
    pictrs_bucket: str = env.str("PICTRS_BUCKET", "pictrs")
    aws_access_key_id: str = env.str("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = env.str("AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = env.str("AWS_DEFAULT_REGION")
    ssh_hostname: str = env.str("SSH_HOSTNAME")
    ssh_port: str = env.int("SSH_PORT", 22)
    ssh_username: str = env.str("SSH_USERNAME")
    ssh_privkey: str = env.str("SSH_PRIVKEY")
    fediverse_safety_worker_auth: str = env.str("FEDIVERSE_SAFETY_WORKER_AUTH")
    fediverse_safety_imgdir: str = env.str("FEDIVERSE_SAFETY_IMGDIR")
    pictrs_safety_url: str = env.str("PICTRS_SAFETY_URL")
    pictrs_safety_apikey: str = env.str("PICTRS_SAFETY_APIKEY")
    pictrs_files_directory: str = env.str("PICTRS_FILES_DIRECTORY")
    sqlite_filename: str = env.str("SQLITE_FILENAME", "lemmy_safety.db")
    use_new_safety: str = env.bool("USE_NEW_SAFETY", True)

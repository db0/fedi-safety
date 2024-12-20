from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

class Config:
    object_storage_endpoint: str | None = env.str("OBJECT_STORAGE_ENDPOINT", None)
    pictrs_bucket: str = env.str("PICTRS_BUCKET", "pictrs")
    ssh_hostname: str | None = env.str("SSH_HOSTNAME", None)
    ssh_port: str = env.int("SSH_PORT", 22)
    ssh_username: str | None = env.str("SSH_USERNAME", None)
    ssh_privkey: str | None = env.str("SSH_PRIVKEY", None)
    fediverse_safety_worker_auth: str | None = env.str("FEDIVERSE_SAFETY_WORKER_AUTH", None)
    fediverse_safety_imgdir: str | None = env.str("FEDIVERSE_SAFETY_IMGDIR", None)
    pictrs_safety_url: str | None = env.str("PICTRS_SAFETY_URL", None)
    pictrs_safety_apikey: str | None = env.str("PICTRS_SAFETY_APIKEY", None)
    pictrs_files_directory: str | None = env.str("PICTRS_FILES_DIRECTORY", None)
    sqlite_filename: str = env.str("SQLITE_FILENAME", "lemmy_safety.db")
    use_new_safety: bool = env.bool("USE_NEW_SAFETY", True)

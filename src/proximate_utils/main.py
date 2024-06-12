"""Main module for proximate_utils."""

from pathlib import Path

from pykeepass.entry import Entry
from pykeepass.group import Group
from pykeepass.pykeepass import PyKeePass, create_database
from trapper_keeper.util.keegen import KeeAuth
from xdg_base_dirs import xdg_config_home, xdg_state_home, xdg_data_home
from proxmoxer.core import ProxmoxAPI

from proximate_utils.actions import Actions
from proximate_utils.info import Info


class ProximateUtils:
    db: Path = xdg_data_home().joinpath("proxmox/proxmox_secrets.kdbx")
    # TODO: Make embedded kv db optional
    # kv_db: Path = xdg_data_home().joinpath("proxmox/proxmox.sqlite")
    token: Path = xdg_config_home().joinpath("proxmox/proxmox_secrets_token")
    key: Path = xdg_state_home().joinpath("proxmox/proxmox_secrets_key")
    proj_id = "a1c4dc95-9801-4262-8b63-012f0460240b"

    # TODO: Return data class as a detached record from Entry
    @classmethod
    def _get_api_secrets(cls, db: PyKeePass) -> Entry:
        proj_group: Group = db.find_groups(recursive=True, name=cls.proj_id, first=True)
        return [host for host in proj_group.entries if host.title == "proxmox_api"][0]

    def __init__(self, db: Path = db, token: Path = token, key: Path = key):
        kee_auth: KeeAuth = KeeAuth()
        kee_auth.kp_key = key
        kee_auth.kp_token = token
        # TODO: Bug if files already exist
        if not kee_auth.kp_token[0].exists():
            kee_auth.save()

        if not db.exists():
            # TODO: Integrate keegen
            # TODO: Bug if token is created but key is not
            # DbUtils.create_tk_store(kp_token=kee_auth.kp_token[1], kp_key=kee_auth.kp_token[1], kp_fp=db, kv_fp=kv_db)
            create_database(filename=db, password=kee_auth.kp_token[1], keyfile=kee_auth.kp_key[0])

        self.proximate_store: PyKeePass = PyKeePass(filename=db, password=token.read_text(encoding="utf-8"), keyfile=key)
        self.proxmox_secrets: Entry = self._get_api_secrets(self.proximate_store)
        self.proxmox: ProxmoxAPI = ProxmoxAPI(
            str(self.proxmox_secrets.url).strip("https://"),
            user=self.proxmox_secrets.username,
            password=self.proxmox_secrets.password,
            verify_ssl=True,
        )

        # TODO: load values from a csv or something into the secure store

        self.info: Info = Info(self.proxmox)
        self.actions: Actions = Actions(self.proxmox)


if __name__ == "__main__":
    prox_utils = ProximateUtils()

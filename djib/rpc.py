import base64
import json
import random
from os import path, stat

import requests
from magic import Magic

from djib.dtypes import *
from djib.kms import KmsClient, request, parse, Ok, PEERS_ENDPOINT


class DjibRpc:
    _kms: KmsClient = None
    _rpc_url: str = None

    def __init__(self, wallet_private_key: str, is_devnet: bool = False, rpc_url: str = None):
        """ constructor
            :param wallet_private_key: str
            :param is_devnet: bool
        """
        self._kms = KmsClient(wallet_private_key, is_devnet=is_devnet)
        if rpc_url is None:
            self._set_peer(is_devnet)
        else:
            self._rpc_url = rpc_url

    def _call_rpc(self, params: list, method: str) -> RPCResponse:
        """ calling KMS API
            :param params: list
            :param method: str
            :return:
        """
        try:
            d = self._kms.encrypt(json.dumps(params))
            res = requests.post(self._rpc_url, json=request(method, [self._kms.wallet_public_key, d]))
            if res.status_code >= 500:
                raise Exception(f"{self._rpc_url} is DOWN!")
            if res.status_code >= 400:
                raise Exception("Bad request!")
            if res.status_code == 200:
                rpc_response = parse(res.json())
                n = RPCResponse()
                if isinstance(rpc_response, Ok):
                    n.data = self._kms.decrypt(rpc_response.result)
                    return n
                n.error = {
                    "message": rpc_response.message,
                    "data": rpc_response.data,
                    "code": rpc_response.code,
                }
                return n
            raise Exception("Unknown Error!")
        except Exception as e:
            raise e

    def _set_peer(self, is_devnet: bool):
        try:
            res = requests.get(PEERS_ENDPOINT + ('relay' if not is_devnet else 'devnet'))
            if res.status_code >= 500:
                raise Exception(f"{PEERS_ENDPOINT} is DOWN!")
            if res.status_code >= 400:
                raise Exception("Bad request!")
            if res.status_code == 200:
                self._rpc_url = random.choice(res.json())['dn']
                return
            raise Exception("Unknown Error!")
        except Exception as e:
            raise e

    def estimate(self, storage_unit: StorageUnit = StorageUnit.GB, storage_size: float = 1) -> RPCResponse:
        """ estimation of djib storage
            :param storage_unit: StorageUnit
            :param storage_size: float
            :return: RPCResponse
        """
        res = self._call_rpc([storage_size, storage_unit], "estimate")
        if not res.error:
            res.data = float(res.data)
        return res

    def status(self) -> RPCResponse:
        """ get status of drive
            :return:
        """
        res = self._call_rpc(["status"], "status")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def create_storage_payment(self, storage_unit: StorageUnit = StorageUnit.GB,
                               storage_size: float = 1) -> RPCResponse:
        """ create storage buy payment
            :param storage_unit: StorageUnit
            :param storage_size: float
            :return: RPCResponse
        """
        res = self._call_rpc([storage_size, storage_unit], "createPayment")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def confirm_storage_payment(self, tracking_code: str) -> RPCResponse:
        """ confirming a storage payment status
            :param tracking_code: str
            :return: RPCResponse
        """
        res = self._call_rpc([tracking_code], "confirmPayment")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def buy_storage(self, tracking_code: str = None, storage_unit: StorageUnit = StorageUnit.GB,
                    storage_size: float = 1) -> RPCResponse:
        """ buy storage with credit or a confirmed payment
            :param storage_size: float
            :param storage_unit: str
            :param tracking_code: str
            :return: RPCResponse
        """
        return self._call_rpc([{
            "tracking_code": tracking_code,
            "size": storage_size,
            "unit": storage_unit,
            "ref_code": None
        }], "buyStorage")

    def ls_drive(self, path_: str = "/") -> RPCResponse:
        """ list drive objects on required path
            :param path_: str
            :return: RPCResponse
        """
        res = self._call_rpc([path_], "lsDrive")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def destroy_drive(self) -> RPCResponse:
        """ destroy drive
            :return: RPCResponse
        """
        return self._call_rpc(["destroyDrive"], "destroyDrive")

    def search(self, query: str, options: SearchOptions = None) -> RPCResponse:
        """ search on drive
            :param query: str
            :param options: SearchOptions
            :return: RPCResponse
        """
        params = [query]
        if (o := options.to_dict()) is not None:
            params.append(o)
        res = self._call_rpc(params, "search")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def create_folder(self, path_: str = "/", name: str = "New Folder") -> RPCResponse:
        """ create new folder
            :param name: str
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_, name], "createFolder")

    def rename(self, path_: str, new_name: str) -> RPCResponse:
        """ rename an object
            :param new_name: str
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_, new_name], "rename")

    def move(self, path_: str, new_dir: str) -> RPCResponse:
        """ move an object
            :param new_dir: str
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_, new_dir], "move")

    def copy(self, path_: str, new_dir: str) -> RPCResponse:
        """ copy an object
            :param new_dir: str
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_, new_dir], "copy")

    def duplicate(self, path_: str) -> RPCResponse:
        """ duplicate an object
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_], "duplicate")

    def ls_recent(self) -> RPCResponse:
        """ list recent objects on drive
            :return: RPCResponse
        """
        res = self._call_rpc(["recentFiles"], "recentFiles")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def ls_favorite(self) -> RPCResponse:
        """ list favorite objects on drive
            :return: RPCResponse
        """
        res = self._call_rpc(["lsFavorite"], "lsFavorite")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def set_favorite(self, path_: str) -> RPCResponse:
        """ set an object to favorite list
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_], "setFavorite")

    def unset_favorite(self, path_: str) -> RPCResponse:
        """ unset an object to favorite list
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_], "unsetFavorite")

    def create_nft_payment(self, count: int = 1) -> RPCResponse:
        """ create save as nft payment
            :param count: int
            :return: RPCResponse
        """
        res = self._call_rpc([count], "createNftPayment")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def confirm_nft_payment(self, tracking_code: str) -> RPCResponse:
        """ confirming a nft payment status
            :param tracking_code: str
            :return: RPCResponse
        """
        res = self._call_rpc([tracking_code], "confirmPayment")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def save_as_nft(self, path_: str, metadata: NftMetaData, receiver_wallet: str = None) -> RPCResponse:
        """ save a file as nft
            :param receiver_wallet: str
            :param metadata: NftMetaData
            :param path_: str
            :return: RPCResponse
        """
        params = [path_, metadata.to_dict()]
        if receiver_wallet:
            params.append(receiver_wallet)
        res = self._call_rpc(params, "saveAsNft")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def ls_nfts(self) -> RPCResponse:
        """ list nft objects
            :return: RPCResponse
        """
        res = self._call_rpc(["lsNfts"], "lsNfts")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def ls_nft_families(self) -> RPCResponse:
        """ list nft families
            :return: RPCResponse
        """
        res = self._call_rpc(["lsNftFamilies"], "lsNftFamilies")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def upload_nft_asset(self, cid: str, saved_at: str, tracking_code: str = None) -> RPCResponse:
        """ complete saving nft process
            :param cid: str
            :param saved_at: str
            :param tracking_code: str
            :return: RPCResponse
        """
        params = [cid, saved_at]
        if tracking_code:
            params.append(tracking_code)
        res = self._call_rpc(params, "uploadAsset")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def prepare_upload(self, path_: str, metadata: UploadFileMetadata) -> RPCResponse:
        """ prepare file for uploading
            :param path_: str
            :param metadata: UploadFileMetadata
            :return: RPCResponse
        """
        res = self._call_rpc([path_, metadata.to_dict()], "prepareUpload")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def upload_private(self, tracking_code: str, index: int, total: int, binary: str) -> RPCResponse:
        """ upload file chunk based
            :param tracking_code: str
            :param index: int
            :param total: int
            :param binary: str
            :return: RPCResponse
        """
        return self._call_rpc([tracking_code, index, total, binary], "privateUpload")

    def prepare_download(self, path_: str) -> RPCResponse:
        """ prepare file for downloading
            :param path_: str
            :return: RPCResponse
        """
        res = self._call_rpc([path_], "prepareDownload")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def download_private(self, tracking_code: str, index: int, total: int) -> RPCResponse:
        """ download file chunk based
            :param tracking_code: str
            :param index: int
            :param total: int
            :return: RPCResponse
        """
        return self._call_rpc([tracking_code, index, total], "privateDownload")

    def ls_trash(self) -> RPCResponse:
        """ list trash files
            :return: RPCResponse
        """
        res = self._call_rpc(["lsTrash"], "lsTrash")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def move_trash(self, path_list: List[str]) -> RPCResponse:
        """ move to trash
            :param path_list: List[str]
            :return: RPCResponse
        """
        return self._call_rpc([path_list], "moveTrash")

    def empty_trash(self) -> RPCResponse:
        """ remove all trash files permanently
            :return: RPCResponse
        """
        return self._call_rpc(["emptyTrash"], "emptyTrash")

    def delete_trash(self, path_: str, deleted_at: str) -> RPCResponse:
        """ remove trash file permanently
            :param path_: str
            :param deleted_at: str
            :return: RPCResponse
        """
        return self._call_rpc([path_, deleted_at], "deleteTrash")

    def restore_from_trash(self, path_: str, deleted_at: str) -> RPCResponse:
        """ restore trash file
            :param path_: str
            :param deleted_at: str
            :return: RPCResponse
        """
        return self._call_rpc([path_, deleted_at], "restoreFromTrash")

    def ls_public(self, just_public: bool = False) -> RPCResponse:
        """ list public objects
            :param just_public: bool
            :return: RPCResponse
        """
        res = self._call_rpc(["lsPublic", just_public], "lsPublic")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def share_to_public(self, path_: str) -> RPCResponse:
        """ share file from private drive on public network ipfs
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_], "shareFromDrive")

    def save_public_file_to_drive(self, cids: List[str], path_: str) -> RPCResponse:
        """ save public files in a directory of private drive
            :param cids: List[str]
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([cids, path_], "savePublic")

    def share_file(self, path_: str, metadata: SharingMetadata = None) -> RPCResponse:
        """ share a file
            :param path_: str
            :param metadata: SharingMetadata
            :return: RPCResponse
        """
        params = [path_]
        if metadata:
            params.append(metadata.to_dict())
        return self._call_rpc(params, "shareObject")

    def ls_file_sharing(self, path_: str) -> RPCResponse:
        """ list all file sharing records
            :param path_: str
            :return: RPCResponse
        """
        res = self._call_rpc([path_], "lsFileShares")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def revoke_file_sharing(self, path_: str, links: List[str]) -> RPCResponse:
        """ revoke a list of sharing records on a file
            :param links: List[str]
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_, links], "revokeShares")

    def ls_shared_with_me(self, metadata: SharedWithMeMetadata = None) -> RPCResponse:
        """ list all shared with me
            :param metadata: SharedWithMeMetadata
            :return: RPCResponse
        """
        params = ["lsShareWithMe"]
        if metadata:
            params.append(metadata.to_dict())
        res = self._call_rpc(params, "lsShareWithMe")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def ls_shared_by_me(self) -> RPCResponse:
        """ list all shared by me
            :return: RPCResponse
        """
        res = self._call_rpc(["lsShareByMe"], "lsShareByMe")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def get_shared_by_link(self, link: str, metadata: GetSharedLinkMetadata = None) -> RPCResponse:
        """ get a shared object by link
            :param metadata: GetSharedLinkMetadata
            :param link: str
            :return: RPCResponse
        """
        params = [link]
        if metadata:
            params.append(metadata.to_dict())
        res = self._call_rpc(params, "getSharedByLink")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def remove_shared_with_me(self, path_: str, owner_email: str) -> RPCResponse:
        """ remove a shared with me record
            :param owner_email: str
            :param path_: str
            :return: RPCResponse
        """
        return self._call_rpc([path_, owner_email], "rmSharedWithMe")

    def prepare_download_shared(self, path_: str, link: str, owner: str, password: str = None) -> RPCResponse:
        """ prepare file for downloading
            :param password: str
            :param path_: str
            :param link: str
            :param owner: str
            :return: RPCResponse
        """
        res = self._call_rpc([path_, link, owner, password], "prepareDownloadShared")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def save_profile(self, metadata: ProfileMetadata) -> RPCResponse:
        """ save profile info
            :param metadata: ProfileMetadata
            :return: RPCResponse
        """
        return self._call_rpc([metadata.to_dict()], "setProfile")

    def get_profile(self) -> RPCResponse:
        """ get profile info
            :return: RPCResponse
        """
        res = self._call_rpc(["getProfile"], "getProfile")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def resend_verification_email(self) -> RPCResponse:
        """ resend verification email
            :return: RPCResponse
        """
        return self._call_rpc(["resendVerificationEmail"], "resendVerificationEmail")

    def confirm_email(self, token: str) -> RPCResponse:
        """ confirm email
            :param token: str
            :return: RPCResponse
        """
        res = self._call_rpc([token], "confirmEmail")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def claim_prizes(self) -> RPCResponse:
        """ claiming all prizes
            :return: RPCResponse
        """
        return self._call_rpc(["claimPrize"], "claimPrize")

    def ls_payments(self) -> RPCResponse:
        """ list payment history
            :return: RPCResponse
        """
        res = self._call_rpc(["lsPayments"], "lsPayments")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def ls_daily_balance(self, days_ago: int = 7) -> RPCResponse:
        """ list daily balance of credit
            :return: RPCResponse
        """
        res = self._call_rpc(["lsDailyBalance", days_ago], "lsDailyBalance")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def create_top_up_payment(self, amount: float = 1) -> RPCResponse:
        """ crating payment url for topping up
            :return: RPCResponse
        """
        res = self._call_rpc([amount], "createTopUpPayment")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def confirm_top_up_payment(self, tracking_code: str) -> RPCResponse:
        """ confirming payment url for topping up
            :param tracking_code: str
            :return: RPCResponse
        """
        res = self._call_rpc([tracking_code], "confirmTopUpPayment")
        if not res.error:
            res.data = json.loads(res.data)
        return res

    def upload_file(self, path_on_local: str, path_on_drive: str) -> RPCResponse:
        """ full cycle upload file
            :param path_on_local: str
            :param path_on_drive: str
            :return: RPCResponse
        """
        if not path.exists(path_on_local):
            raise Exception(f"{path_on_local} doesn't exist!")
        if not path.isfile(path_on_local):
            raise Exception(f"{path_on_local} isn't a file!")
        metadata = UploadFileMetadata()
        metadata.file_name = path_on_local.split(path.sep)[-1]
        metadata.size_byte = stat(path_on_local)
        metadata.content_type = Magic(mime=True).from_file(path_on_local)
        response = self.prepare_upload(path_on_drive, metadata)
        if response.error:
            return response
        tracking_code = response.data['tracking_code']
        total = response.data['total']
        index = 0
        chunks = response.data['chunk']
        file = open(path_on_local, 'rb')
        while index != total:
            file.seek(index * chunks)
            binary = base64.b64encode(file.read(chunks)).decode('utf-8')
            response = self.upload_private(tracking_code, index + 1, total, binary)
            if response.error:
                return response
            index += 1
        file.close()

    def download_file(self, path_on_local: str, path_on_drive: str, is_shared: bool = False, link: str = None,
                      owner: str = None, password: str = None) -> RPCResponse:
        """ full cycle download file
            :param password: str
            :param owner: str
            :param link: str
            :param is_shared: bool
            :param path_on_local: str
            :param path_on_drive: str
            :return: RPCResponse
        """
        if not path.exists(path_on_local):
            raise Exception(f"{path_on_local} doesn't exist!")
        if path.isfile(path_on_local):
            raise Exception(f"{path_on_local} is a file!")
        if not is_shared:
            response = self.prepare_download(path_on_drive)
        else:
            response = self.prepare_download_shared(path_on_drive, link, owner, password)
        if response.error:
            return response
        file_name = response.data['file_name']
        tracking_code = response.data['tracking_code']
        total = response.data['total']
        index = 0
        chunks = response.data['chunk']
        file = open(f"{path_on_local}{path.sep}{file_name}", 'wb')
        while index != total:
            file.seek(index * chunks)
            response = self.download_private(tracking_code, index + 1, total)
            if response.error:
                return response
            binary = base64.b64decode(response.data)
            file.write(binary)
            index += 1
        file.close()

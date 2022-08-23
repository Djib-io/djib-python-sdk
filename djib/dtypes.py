from typing import Any, List


class RPCResponse:
    error: dict = None
    data: Any = None


class StorageUnit:
    KB: str = 'KB'
    MB: str = 'MB'
    GB: str = 'GB'
    TB: str = 'TB'


class SearchOptions:
    extension: str = None
    path: str = None

    def to_dict(self):
        o = {}
        if self.extension:
            o['extension'] = self.extension
        if self.path:
            o['path'] = self.path
        if o != {}:
            return o
        return None


class NftAttribute:
    trait_type: str = "Power"
    value: str = "Rare"

    def to_dict(self):
        return {"trait_type": self.trait_type, "value": self.value}


class NftMetaData:
    thumbnail_cid: str = None
    name: str = 'Djib NFT'
    symbol: str = 'DJIB'
    description: str = 'Sample Djib NFT'
    seller_fee_basis_points: int = 0
    external_url: str = 'https://djib.io'
    attributes: List[NftAttribute]
    collection: str
    family: str

    def to_dict(self):
        return {
            "thumbnail": self.thumbnail_cid,
            "name": self.name,
            "symbol": self.symbol,
            "description": self.description,
            "seller_fee_basis_points": self.seller_fee_basis_points,
            "external_url": self.external_url,
            "attributes": [x.to_dict() for x in self.attributes],
            "collection": self.collection,
            "family": self.family
        }


class UploadFileMetadata:
    file_name: str = None
    size_byte: int = 0
    content_type: str = None

    def to_dict(self):
        return {
            "file_name": self.file_name,
            "size_byte": self.size_byte,
            "content_type": self.content_type,
        }


class SharingMetadata:
    password: str = None
    email: str = None

    def to_dict(self):
        o = {}
        if self.email:
            o['email'] = self.email
        if self.password:
            o['password'] = self.password
        if o != {}:
            return o
        return None


class SharedWithMeMetadata:
    password: str = None
    path: str = None
    owner: str = None

    def to_dict(self):
        o = {}
        if self.path:
            o['path'] = self.path
        if self.password:
            o['password'] = self.password
        if self.owner:
            o['owner'] = self.owner
        if o != {}:
            return o
        return None


class GetSharedLinkMetadata:
    password: str = None
    path: str = None

    def to_dict(self):
        o = {}
        if self.path:
            o['path'] = self.path
        if self.password:
            o['password'] = self.password
        if o != {}:
            return o
        return None


class ProfileMetadata:
    email: str = None
    name: str = None
    avatar: str = None

    def to_dict(self):
        o = {}
        if self.email:
            o['email'] = self.email
        if self.name:
            o['name'] = self.name
        if self.avatar:
            o['avatar'] = self.avatar
        if o != {}:
            return o
        return None

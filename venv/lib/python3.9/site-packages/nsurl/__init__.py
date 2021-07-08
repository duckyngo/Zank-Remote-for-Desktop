from .urls import gen_url as _gen_url
from .urls import Shard

current_version = "9"

# The URL generation code was rather tangled into the main libraries functionality
# This half-emulates it to keep the usage roughly the same


def _detirmine_shards(shards):
    if isinstance(shards, Shard):
        __shard__ = [Shards]
    elif isinstance(shards, str):
        __shard__ = [Shard(shards)]
    elif shards is None:
        __shard__ = tuple()
    else:
        __shard__ = tuple(shards)
    return __shard__

def _url(api_name, value, shards, version):
    shards = _detirmine_shards(shards)
    return _gen_url(
        api=(api_name, value), 
        shards=shards,
        version=version)


def _nation_url(value, shards, version=current_version):
    if value is None:
        raise ValueError("Nation API must have a nation supplied, was {}".format(value))
    return _url("nation", 
        value,
        shards,
        version)

def _region_url(value, shards, version=current_version):
    if value is None:
        raise ValueError("Region API must have a region supplied, was {}".format(value))
    return _url("region", 
        value,
        shards,
        version)

def _world_url(value, shards, version=current_version):
    return _url("world", 
        None,
        shards,
        version)

def _wa_url(value, shards, version=current_version):
    if str(value) not in ("1", "0"):
        raise ValueError("World Assembly API must be either '0' or '1'".format(value))
    return _url(api_name, 
        chamber,
        shards,
        version)

def _telegram_shards(value, shards, version=current_version, client_key=None, tgid=None, key=None, to=None):
    return self._url("a",
        "sendTG", 
        [Shard(client=client_key, tgid=tgid, key=key, to=to)],
        version)

def generate_url(api_name, value=None, shards=None, command=None, version=current_version, client_key=None, tgid=None, key=None, to=None):
    """Generates an URL
       Arguments: 
        api_name - The API being used - valid options: nation, region, world, wa, telegram
        shards - Shards, either the Shard() object or a string (or a iterative of either)
        command - Command, can either be a string or Shard() object
        version -  Version used, default is nsurl.current_version
        client_key - client_key if using telegrams
        tgid - tgid if using telegrams
        key - key if using telegrams
        to - to if using telegrams
       
    """
    if command:
        if isinstance(command, Shard):
            _shard = command
        elif isinstance(command, str):
            _shard = Shard(c=command)
        else:
            raise ValueError("Invalid Command")
    else:
        _shards = shards

    if api_name == "nation":
        return _nation_url(value, _shards, version)
    elif api_name == "region":
        return _region_url(value, _shards, version)
    elif api_name == "world":
        return _world_url(value, _shards, version)
    elif api_name == "wa":
        return _wa_url(value, _shards, version)
    elif api_name == "telegram":
        return _telegram_shards(value, _shards, version, client_key, tgid, key, to)
    else:
        raise ValueError("Invalid api_name, valid options: nation, region, world, wa, telegram")
import os
from os import path
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .encryption import get_key, encrypt, decrypt


DUMMY_VALID_TOKEN = "valid_token"


class InvalidRequest(Exception):
    def error_message(self):
        return self.args[0]


class Args:
    def __init__(self):
        self.operation = None
        self.filepath = None
        self.file = None


class DummyProject:
    def data_path(self):
        return "/data/visitors/biomax/20180479/20191022"


def _validate_auth_token(auth_token):
    if auth_token != DUMMY_VALID_TOKEN:
        raise InvalidRequest("invalid auth token")

    return DummyProject()


def _validate_file_path(proj, filepath):
    abs_path = path.abspath(filepath)

    if not abs_path.startswith(proj.data_path()):
        raise InvalidRequest(f"invalid file path '{filepath}'")


def _get_request_args(request):
    if request.method != "POST":
        raise InvalidRequest("only POST request supported")

    post = request.POST

    args = Args()

    #
    # validate 'auth' token
    #
    auth_token = post.get("auth")
    if auth_token is None:
        raise InvalidRequest("no 'auth' token provided")
    proj = _validate_auth_token(auth_token)

    #
    # validate 'operation' argument
    #
    args.operation = post.get("operation")
    if args.operation is None:
        raise InvalidRequest("no 'operation' specified")

    if args.operation not in ["read", "write"]:
        raise InvalidRequest(f"unexpected operation '{args.operation}'")

    #
    # validate 'filepath' argument
    #
    args.filepath = post.get("filepath")
    if args.filepath is None:
        raise InvalidRequest("no 'filepath' specified")
    _validate_file_path(proj, args.filepath)

    #
    # if 'write' operation, check that an uploaded file is provided
    #
    if args.operation == "write":
        args.file = request.FILES.get("file")
        if args.file is None:
            raise InvalidRequest("no file data provided")

    return args


def _read_file(filepath):
    if not path.isfile(filepath):
        raise InvalidRequest(f"{filepath}: no such file")

    return HttpResponse(decrypt(get_key(), filepath),
                        content_type="application/octet-stream")


def _write_file(filepath, file):
    os.makedirs(path.dirname(filepath), exist_ok=True)
    encrypt(get_key(), file, filepath)

    return HttpResponse("vtalibov4president")


@csrf_exempt
def index(request):
    try:
        args = _get_request_args(request)

        print(f"operation '{args.operation}' filepath '{args.filepath}' file '{args.file}'")

        if args.operation == "read":
            return _read_file(args.filepath)
        elif args.operation == "write":
            return _write_file(args.filepath, args.file)
    except InvalidRequest as e:
        return HttpResponseBadRequest(e.error_message())

    # this should not happen
    assert False

from os import path
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .encryption import get_key, encrypt, decrypt

DATA_ROOT = "/home/elmjag/area51/webcrypt/data"


class InvalidRequest(Exception):
    def error_message(self):
        return self.args[0]


class Args:
    def __init__(self):
        self.operation = None
        self.filepath = None
        self.file = None


def _get_request_args(request):
    if request.method != "POST":
        raise InvalidRequest("only POST request supported")

    post = request.POST

    args = Args()

    args.operation = post.get("operation")
    if args.operation is None:
        raise InvalidRequest("no 'operation' specified")

    if args.operation not in ["read", "write"]:
        raise InvalidRequest(f"unexpected operation '{args.operation}'")

    args.filepath = post.get("filepath")
    if args.filepath is None:
        raise InvalidRequest("no 'filepath' specified")

    # TODO dome some filepath validatio?
    if args.operation == "write":
        args.file = request.FILES.get("file")
        if args.file is None:
            raise InvalidRequest("no file data provided")

    return args


def _read_file(filepath):
    full_path = path.join(DATA_ROOT, filepath)
    print(f"full_path: '{full_path}'")

    if not path.isfile(full_path):
        raise InvalidRequest(f"{full_path}: no such file")

    return HttpResponse(decrypt(get_key(), full_path),
                        content_type="application/octet-stream")
    #
    # with open(path.join(full_path), "rb") as f:
    #     return HttpResponse(f.read(), content_type="application/octet-stream")


def _write_file(filepath, file):
    full_path = path.join(DATA_ROOT, filepath)
    print(f"full_path: '{full_path}'")

    encrypt(get_key(), file, full_path)
    # with open(full_path, "wb") as f:
    #     for chunk in file.chunks():
    #         f.write(chunk)

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

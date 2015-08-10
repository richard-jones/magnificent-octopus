from octopus.core import app
import requests, time, urllib

class SizeExceededException(Exception):
    pass

def quote(s, **kwargs):
    try:
        return urllib.quote_plus(s, **kwargs)
    except:
        pass

    try:
        utf = s.encode("utf-8")
        return urllib.quote(utf, **kwargs)
    except:
        return None

def _backoff(attempt_number, back_off_factor, max_back_off):
    seconds = 2**attempt_number * back_off_factor
    seconds = seconds if seconds < max_back_off else max_back_off
    return seconds

def _make_request(method, url,
                  retries=None, back_off_factor=None, max_back_off=None, timeout=None, response_encoding=None,
                  retry_on_timeout=None, retry_codes=None,
                  **kwargs):

    # fill out all the default arguments
    if retries is None:
        retries = app.config.get("HTTP_MAX_RETRIES", 0)

    if back_off_factor is None:
        back_off_factor = app.config.get("HTTP_BACK_OFF_FACTOR", 1)

    if max_back_off is None:
        max_back_off = app.config.get("HTTP_MAX_BACK_OFF", 30)

    if timeout is None:
        timeout = app.config.get("HTTP_TIMEOUT", 30)

    if retry_on_timeout is None:
        retry_on_timeout = app.config.get("HTTP_RETRY_ON_TIMEOUT", True)

    if retry_codes is None:
        retry_codes = app.config.get("HTTP_RETRY_CODES", [])

    if response_encoding is None:
        response_encoding = app.config.get("HTTP_RESPONSE_ENCODING")

    attempt = 0
    r = None

    while attempt <= retries:
        try:
            if method == "GET":
                r = requests.get(url, timeout=timeout, **kwargs)
            elif method == "POST":
                r = requests.post(url, timeout=timeout, **kwargs)
            elif method == "PUT":
                r = requests.put(url, timeout=timeout, **kwargs)
            elif method == "DELETE":
                r = requests.delete(url, timeout=timeout, **kwargs)
            else:
                # FIXME: is this right?  Maybe raising an exception would be better
                app.logger.debug("Method {method} not allowed".format(method=method))
                return None

            if r.status_code not in retry_codes:
                break
            else:
                attempt += 1
                app.logger.debug("Request to {url} resulted in status {status}, attempt {attempt}".format(status=r.status_code, url=url, attempt=attempt))
        except requests.exceptions.Timeout:
            attempt += 1
            app.logger.debug('Request to {url} timeout, attempt {attempt}'.format(url=url, attempt=attempt))
            if not retry_on_timeout:
                break

        bo = _backoff(attempt, back_off_factor, max_back_off)
        app.logger.debug('Request to {url} backing off for {bo} seconds'.format(url=url, bo=bo))
        time.sleep(bo)

    if response_encoding is not None and r is not None:
        r.encoding = 'utf-8'

    return r

def put(url, retries=None, back_off_factor=None, max_back_off=None, timeout=None, response_encoding=None,
         retry_on_timeout=None, retry_codes=None, **kwargs):
    return _make_request("PUT", url,
                         retries=retries, back_off_factor=back_off_factor,
                         max_back_off=max_back_off,
                         timeout=timeout,
                         response_encoding=response_encoding,
                         retry_on_timeout=retry_on_timeout,
                         retry_codes=retry_codes,
                         **kwargs)

def delete(url, retries=None, back_off_factor=None, max_back_off=None, timeout=None, response_encoding=None,
         retry_on_timeout=None, retry_codes=None, **kwargs):
    return _make_request("DELETE", url,
                         retries=retries, back_off_factor=back_off_factor,
                         max_back_off=max_back_off,
                         timeout=timeout,
                         response_encoding=response_encoding,
                         retry_on_timeout=retry_on_timeout,
                         retry_codes=retry_codes,
                         **kwargs)

def post(url, retries=None, back_off_factor=None, max_back_off=None, timeout=None, response_encoding=None,
         retry_on_timeout=None, retry_codes=None, **kwargs):
    return _make_request("POST", url,
                         retries=retries, back_off_factor=back_off_factor,
                         max_back_off=max_back_off,
                         timeout=timeout,
                         response_encoding=response_encoding,
                         retry_on_timeout=retry_on_timeout,
                         retry_codes=retry_codes,
                         **kwargs)

def get(url, retries=None, back_off_factor=None, max_back_off=None, timeout=None, response_encoding=None,
        retry_on_timeout=None, retry_codes=None, **kwargs):
    return _make_request("GET", url,
                         retries=retries, back_off_factor=back_off_factor,
                         max_back_off=max_back_off,
                         timeout=timeout,
                         response_encoding=response_encoding,
                         retry_on_timeout=retry_on_timeout,
                         retry_codes=retry_codes,
                         **kwargs)

def get_stream(url, retries=None, back_off_factor=None, max_back_off=None, timeout=None, response_encoding=None,
        retry_on_timeout=None, retry_codes=None, size_limit=None, chunk_size=None, cut_off=None, **kwargs):

    # set the defaults where necessary from configuration

    if size_limit is None:
        size_limit = app.config.get("HTTP_STREAM_MAX_SIZE", 0)  # size of 0 means no limit

    if cut_off is None:
        cut_off = app.config.get("HTTP_STREAM_CUT_OFF", 0)  # size of 0 means no limit

    if chunk_size is None:
        chunk_size = app.config.get("HTTP_STREAM_CHUNK_SIZE", 262144)   # 250Kb

    # actually make the request (note that we pass stream=True)
    resp = _make_request("GET", url,
             retries=retries, back_off_factor=back_off_factor,
             max_back_off=max_back_off,
             timeout=timeout,
             response_encoding=response_encoding,
             retry_on_timeout=retry_on_timeout,
             retry_codes=retry_codes,
             stream=True,
             **kwargs)

    if resp is None:
        return None, "", 0

    # check that content length header for an early view on whether the resource
    # is too large
    if size_limit > 0:
        header_reported_size = resp.headers.get("content-length")
        try:
            header_reported_size = int(header_reported_size)
        except Exception as e:
            header_reported_size = 0

        if header_reported_size > size_limit:
            resp.connection.close()
            raise SizeExceededException("Size as announced by Content-Type header is larger than maximum allowed size")

    downloaded_bytes = 0
    content = ''
    chunk_no = 0

    for chunk in resp.iter_content(chunk_size=chunk_size):
        chunk_no += 1
        downloaded_bytes += len(bytes(chunk))

        # check the size limit again
        if size_limit > 0 and downloaded_bytes > size_limit:
            resp.connection.close()
            raise SizeExceededException("Size limit exceeded during download")
        if chunk:  # filter out keep-alive new chunks
            content += chunk

        # now check to see if we have exceeded the cut off point
        if cut_off > 0 and downloaded_bytes >= cut_off:
            break

    resp.connection.close()
    return resp, content, downloaded_bytes

"""
we don't have immediate use for this, but it will be helpful in the future, so preserving in this block comment
needs to be refactored as per the above method

def get_stream(url):
    r = requests.get(url, stream=True, timeout=config.CONN_TIMEOUT)
    r.encoding = 'utf-8'

    size_limit = config.MAX_REMOTE_FILE_SIZE
    header_reported_size = r.headers.get("content-length")
    try:
        header_reported_size = int(header_reported_size)
    except Exception as e:
        header_reported_size = 0

    if header_reported_size > size_limit:
        return ''

    downloaded_bytes = 0
    content = ''
    chunk_no = 0
    attempt = 0
    retries = config.MAX_CONN_RETRIES
    while attempt <= retries:
        try:
            for chunk in r.iter_content(chunk_size=config.HTTP_CHUNK_SIZE):
                chunk_no += 1
                downloaded_bytes += len(bytes(chunk))

                if chunk_no == 1:
                    if magic.from_buffer(chunk).startswith('PDF'):
                        raise models.LookupException('File at {0} is a PDF according to the python-magic library. Not allowed!'.format(url))

                # check the size limit again
                if downloaded_bytes > size_limit:
                    raise models.LookupException('File at {0} is larger than limit of {1}'.format(url, size_limit))
                if chunk:  # filter out keep-alive new chunks
                    content += chunk
            break

        except socket.timeout:
            attempt += 1
            log.debug('Request to {url} timeout, attempt {attempt}'.format(url=url, attempt=attempt))

        sleep(2 ** attempt)

    r.connection.close()
    return r, content, downloaded_bytes
"""

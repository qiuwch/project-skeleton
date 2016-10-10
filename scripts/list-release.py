import requests, json, os
from pprint import pprint
import pdb
import gitutil

base_url = 'https://api.github.com'
repo_url = '/repos/qiuwch/project-skeleton'
auth = ('username', 'password')

def get(url, **kwargs):
    kwargs['auth'] = auth
    return requests.get(url, **kwargs)

def delete(url, **kwargs):
    kwargs['auth'] = auth
    return requests.delete(url, **kwargs)

def patch(url, **kwargs):
    kwargs['auth'] = auth
    return requests.patch(url, **kwargs)

def post(url, **kwargs):
    kwargs['auth'] = auth
    return requests.post(url, **kwargs)

def query_by_tag_name(data, tag_name):
    ids = [r['id'] for r in data if r['tag_name'] == tag_name]
    assert(len(ids) == 1)
    return ids

def query_by_tag_name1(repo_url, tag_name):
    url = base_url + repo_url + '/releases/tags/' + tag_name
    print url
    r = get(url)
    print r
    if r.status_code in [200]:
        data = json.loads(r.text)
        return data
    else:
        print r
        return None

def list_assets(repo_url, release_id):
    url = base_url + repo_url + '/releases/%s/assets' % release_id
    r = get(url)
    data = json.loads(r.text)
    return data

def get_content_type(filename):
    # import mimetypes
    # mime_type = mimetypes.guess_type(filename)
    # print mime_type
    import magic
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(filename)
    return mime_type

def edit_asset(repo_url, release_id, filename):
    pass

def delete_asset(repo_url, asset_id):
    url = base_url + repo_url + '/releases/assets/%s' % asset_id
    print url
    r = delete(url)
    print r
    print r.text

def patch_asset(repo_url, asset_id):
    args = {
        'name': 'test1.txt'
    }
    url = base_url + repo_url + '/releases/assets/%s' % asset_id
    print url
    r = patch(url, data = args)
    print r
    print r.text

def upload_asset(repo_url, release_id, upload_url, filename):
    filename = os.path.basename(filename)
    # url = upload_url + repo_url + '/releases/%s/assets?name=%s' % (release_id, filename)
    url = 'https://uploads.github.com'+ repo_url + '/releases/%s/assets?name=%s' % (release_id, filename)
    # url = 'http://uploads.github.com'+ repo_url + '/releases/%s/assets?name=%s' % (release_id, filename)
    # http can not work and produce a very strange error
    print url
    content_type = get_content_type(filename)
    print content_type
    content_type = 'text/html'
    args = {
        'Content-Type': content_type, # What if I don't set this manually?
    }
    f = open(filename, 'rb')
    r = requests.post(url, data=f, headers=args, auth=auth)
    print r

    # url = 'http://httpbin.org/post'
    # r = requests.post(url, data=open(filename, 'rb'), headers=args, auth=auth)
    return r

def edit_release(repo_url, release_id, info):
    url = base_url + repo_url + '/releases/%s' % release_id
    print url
    r = patch(url, data=json.dumps(info))
    return r

def create_release(repo_url, info):
    url = base_url + repo_url + '/releases'
    r = post(url, data=json.dumps(info))
    return json.loads(r.text)

def list_releases(repo_url):
    url = base_url + repo_url + '/releases'
    r = get(url)
    release_data = json.loads(r.text)
    # pprint(release_data)
    return r

def print_asset(v):
    keys = ['id', 'name', 'download_count', 'content_type', 'url']
    for k in keys:
        print '%8s : %s' % (k , v[k])

def main():
    git_version = gitutil.get_short_version('.', force=True)
    # r = list_releases(repo_url)
    # print r.text
    # return
    # print query_by_tag_name(release_data, 'nightly-build')
    release_data = query_by_tag_name1(repo_url, 'nightly-build')
    print 'Git version', git_version

    info = {
        'tag_name': 'nightly-build1',
        'name': 'A Nightly build',
        'target_commitish': 'master',
        # 'target_commitish': git_version,
        # 'body': 'Automatically build from the master branch',
        'draft': False,
        'prerelease': True,
    }

    if not release_data:
        # Create a new release
        release_data = create_release(repo_url, info)
    else:
        r = edit_release(repo_url, release_data['id'], info)
        print r.text


    # release_data = query_by_tag_name1(repo_url, 'master')
    assets = list_assets(repo_url, release_data['id'])
    # for v in assets:
    #     print '-' * 80
    #     print_asset(v)
    #     # pprint(v)


    # for v in assets:
    #     delete_asset(repo_url, v['id'])
    #     # patch_asset(repo_url, v['id'])
    #
    release_id = release_data['id']
    upload_url = release_data['upload_url']
    # # print upload_url
    # upload_asset(repo_url, release_id, upload_url, './index.html')

    version_file = '%s.txt' % git_version
    with open(version_file, 'w') as f:
        f.write(git_version)

    upload_asset(repo_url, release_id, upload_url, version_file)


if __name__ == '__main__':
    main()

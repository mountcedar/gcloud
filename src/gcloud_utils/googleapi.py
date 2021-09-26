#!/usr/bin/env python

import os

import logging
import traceback
import pickle

import googleapiclient.discovery
import googleapiclient.http

class GoogleDrive(object):
    '''
    GoogleDrive関係のアクセスをまとめた
    '''
    SCOPES = 'https://www.googleapis.com/auth/drive'

    def __init__(self, drive_service=None, colab=False, credential=None):
        self.credential = credential
        if drive_service is None:
            if colab:
                self.drive_service = self.drive_service_with_colab()
            else:
                self.drive_service = self.drive_service_with_service_account()
        else:
            self.drive_service = drive_service

    def drive_service_with_colab(self):
        import google.colab
        google.colab.auth.authenticate_user()
        return googleapiclient.discovery.build('drive', 'v3')

    def drive_service_with_service_account(self):
        from oauth2client.service_account import ServiceAccountCredentials
        from httplib2 import Http

        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credential, GoogleDrive.SCOPES)
        http_auth = credentials.authorize(Http())
        return googleapiclient.discovery.build('drive', 'v3', http=http_auth)

    def query(self, query):
        """
        Note: this api limit the page size 1000, the perfect algorithm should support next page with pageToken
        See: https://developers.google.com/drive/api/v3/reference/files/list
        """
        return self.drive_service.files().list(q=query, pageSize=1000).execute().get('files')

    def search(self, filename, directory_id=None):
        if directory_id is None:
            return self.query(query="name='%s'" % filename)
        else:
            return self.query(query="name='%s' and '%s' in parents" % (filename, directory_id))

    def list(self, dirname=None, directory_id=None):
        if dirname:
            for entity in self.search(dirname):
                if entity.get('name') == dirname:
                    directory_id = entity.get('id')
                    break
        if directory_id is None:
            return None
        else:
            return self.query(query="'%s' in parents and trashed=false" % directory_id)

    def download(self, filename, parents=[]):
        file_list = self.search(filename)

        file_id = None

        if not parents:
            # ファイル ID を取得します。
            for file in file_list:
              if file.get('name') == filename:
                  file_id = file.get('id')
                  break
        else:
            for entity in self.list(directory_id=parents[0]):
                logging.debug('found %s', entity.get('name'))
                if entity.get('name') == filename:
                    file_id = entity.get('id')
                    break

        if file_id is None:
            # ファイル ID を取得できなかった場合はエラーメッセージを出力します。
            logging.error(filename + ' が見つかりません.')
        else:
            # colab 環境へファイルをアップロードします。
            with open(filename, 'wb') as f:
                request = self.drive_service.files().get_media(fileId=file_id)
                media = googleapiclient.http.MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    progress_status, done = media.next_chunk()
                    print(100 * progress_status.progress())
                    logging.info("%完了")

            logging.debug('Googleドライブからのファイル取り込みが完了しました.')
    
    def upload(self, filename, parents=[], update=True):
        file_id = None

        if not parents:
            for entity in self.search(filename):
                if entity.get('name') == filename:
                    file_id = entity.get('id')
                    break
        else:
            for entity in self.list(directory_id=parents[0]):
                if entity.get('name') == filename:
                    file_id = entity.get('id')
        
        media = googleapiclient.http.MediaFileUpload(
            filename, 
            mimetype='application/octet-stream',
            resumable=True
        )

        if update and not file_id is None:
            file_metadata = {
              'name': filename,
              'mimeType': 'application/octet-stream',
            }
            return self.drive_service.files().update(
                fileId=file_id,
                body=file_metadata,
                # newRevision=True,
                media_body=media,
                # addParents=[file_id,]
            ).execute()
        else:
            file_metadata = {
             'name': filename,
              'mimeType': 'application/octet-stream',
              'parents': parents
            }
            return self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
    
    def create_folder(self, name, directory_id=None):
        # Create a folder on Drive, returns the newely created folders ID
        files = self.search(name, directory_id=directory_id)
        for fobj in files:
            return fobj.get('id')
        body = {
          'name': name,
          'mimeType': "application/vnd.google-apps.folder"
        }
        if parentID:
            body['parents'] = [parentID,]
        root_folder = self.drive_service.files().create(body=body, fields='id').execute()
        return root_folder.get('id')

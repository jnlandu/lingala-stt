import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

def get_or_create_folder(service, folder_name, parent_id=None):
    """Get folder ID or create if it doesn't exist"""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(q=query).execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
    else:
        # Create folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
            
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')

def file_exists_in_drive(service, filename, parent_id):
    """Check if file already exists in Drive"""
    query = f"name='{filename}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query).execute()
    return len(results.get('files', [])) > 0

def upload_to_gdrive():
    try:
        # Load credentials from JSON string
        credentials_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT')
        if not credentials_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT environment variable not set")
        
        # Parse JSON and create credentials
        try:
            credentials_info = json.loads(credentials_json)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in credentials: {e}")
            print(f"First 100 chars of credentials: {credentials_json[:100]}")
            raise
        
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        # Create main folder structure
        main_folder_id = get_or_create_folder(service, 'lingala-stt')
        audio_folder_id = get_or_create_folder(service, 'audio', main_folder_id)
        metadata_folder_id = get_or_create_folder(service, 'metadata', main_folder_id)
        
        uploaded_count = 0
        skipped_count = 0
        
        print("📤 Starting upload to Google Drive...")
        
        # Upload audio files
        audio_dir = 'data/raw/okapi'
        if os.path.exists(audio_dir):
            for filename in os.listdir(audio_dir):
                if filename.endswith('.mp3'):
                    file_path = os.path.join(audio_dir, filename)
                    
                    # Check if file already exists
                    if file_exists_in_drive(service, filename, audio_folder_id):
                        print(f"⏭️  Skipping {filename} (already exists)")
                        skipped_count += 1
                        continue
                    
                    # Upload file
                    media = MediaFileUpload(file_path, mimetype='audio/mpeg')
                    file_metadata = {
                        'name': filename,
                        'parents': [audio_folder_id]
                    }
                    
                    service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    print(f"✅ Uploaded: {filename}")
                    uploaded_count += 1
        
        # Upload metadata files
        metadata_dir = 'data/raw/okapi/metadata'
        if os.path.exists(metadata_dir):
            for filename in os.listdir(metadata_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(metadata_dir, filename)
                    
                    # Check if file already exists
                    if file_exists_in_drive(service, filename, metadata_folder_id):
                        print(f"⏭️  Skipping {filename} (already exists)")
                        skipped_count += 1
                        continue
                    
                    # Upload file
                    media = MediaFileUpload(file_path, mimetype='application/json')
                    file_metadata = {
                        'name': filename,
                        'parents': [metadata_folder_id]
                    }
                    
                    service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    print(f"✅ Uploaded metadata: {filename}")
                    uploaded_count += 1
        
        # Upload manifest file
        manifest_path = 'manifest.json'
        if os.path.exists(manifest_path):
            if not file_exists_in_drive(service, 'manifest.json', main_folder_id):
                media = MediaFileUpload(manifest_path, mimetype='application/json')
                file_metadata = {
                    'name': 'manifest.json',
                    'parents': [main_folder_id]
                }
                
                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                print("✅ Uploaded manifest.json")
                uploaded_count += 1
            else:
                # Update existing manifest
                query = f"name='manifest.json' and '{main_folder_id}' in parents"
                results = service.files().list(q=query).execute()
                if results.get('files'):
                    file_id = results['files'][0]['id']
                    media = MediaFileUpload(manifest_path, mimetype='application/json')
                    service.files().update(fileId=file_id, media_body=media).execute()
                    print("🔄 Updated manifest.json")
        
        print(f"\n📊 Upload Summary:")
        print(f"   • New files uploaded: {uploaded_count}")
        print(f"   • Files skipped: {skipped_count}")
        print(f"   • Google Drive folder: https://drive.google.com/drive/folders/{main_folder_id}")
        
        # Create summary for GitHub Actions
        with open('upload_summary.txt', 'w') as f:
            f.write(f"uploaded={uploaded_count}\n")
            f.write(f"skipped={skipped_count}\n")
            f.write(f"folder_id={main_folder_id}\n")
        
    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        raise
    except Exception as error:
        print(f"❌ Unexpected error: {error}")
        raise

if __name__ == '__main__':
    upload_to_gdrive()
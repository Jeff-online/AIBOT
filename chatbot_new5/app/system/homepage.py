import os
import time
import uuid
import shutil
import chardet
import logging
from app import messages
from . import system_api
from . args_parser import *
from flask import current_app
from datetime import datetime, timedelta
from utils.file_utils import FileOperation
from werkzeug.utils import secure_filename
from common.common_resource import GlobalResource, Resource
logger = logging.getLogger(__name__)


class SessionManagement(GlobalResource):

    def get(self):
        """セッションリスト"""
        args_parser = SessionParser()
        args = args_parser.parser.parse_args()
        username = args.get("username")
        session_id = args.get("session_id")
        if not username:
            raise messages.UserNameNotExistsError
        user_data = list(current_app.container.query_items(
            query=f"SELECT * FROM user u WHERE u.username = '{username}'",
            enable_cross_partition_query=True
        ))
        if user_data:
            user_info = user_data[0]
            user_info_allow = self.check_session(user_info)
            u_sessions = user_info_allow.get("U_session", [])
            if not session_id:
                title_result = [{"session_id": session["session_id"], "title": session["title"]} for session in
                                u_sessions]
                return {"session_data": title_result, "code": 200}
            history_data = list(current_app.container_c.query_items(
                query=f"SELECT * FROM user s WHERE s.session_id = '{session_id}'",
                enable_cross_partition_query=True
            ))
            if history_data:
                history_info = history_data[0]
                return {"content_data": history_info["S_info"], "code": 200}
            return {"msg": "データ存在しない", "code": 404}
        else:
            raise messages.UserNotExistsError

    def post(self):
        """セッション内容の追加"""
        args_parser = SessionAddParser()
        args = args_parser.parser.parse_args()
        username = args.get("username")
        if not username:
            raise messages.UserNameNotExistsError
        user_data = list(current_app.container.query_items(
            query=f"SELECT * FROM user u WHERE u.username = '{username}'",
            enable_cross_partition_query=True
        ))
        if user_data:
            session_id = str(uuid.uuid4())
            user_info = user_data[0]
            session_data = {
                "session_id": session_id,
                "title": "新しい会話",
                "create_time": datetime.now().isoformat()
            }
            user_sessions = user_info.get("U_session", [])
            user_sessions.append(session_data)
            user_info["U_session"] = user_sessions
            current_app.container.upsert_item(user_info)

            history_data = {
                "id": session_id,
                "session_id": session_id,
                "S_info": {"content": []}
            }
            current_app.container_c.upsert_item(history_data)

            session_info = {
                "session_id": session_data["session_id"]
            }
            logger.info("New Session Successful")
            return {'session_info': session_info, 'code': 200}
        else:
            raise messages.UserNotExistsError

    def put(self):
        """セッションの変更"""
        args_parser = SessionPutParser()
        args = args_parser.parser.parse_args()
        username = args.get("username")
        prompt_name = args.get("prompt_name")
        attachment_names = args.get("attachment_name")
        contents = args.get("content")
        session_id = args.get("session_id")
        if not username:
            raise messages.UserNameNotExistsError
        user_data = list(current_app.container.query_items(
            query=f"SELECT * FROM user u WHERE u.username = '{username}'",
            enable_cross_partition_query=True
        ))
        if user_data:
            user_info = user_data[0]
            try:
                clue, file_contents = self.check_name(prompt_name, username, attachment_names)
            except Exception as e:
                return {"message": str(e), "status": 404}
            dialogue_history = [{"role": "system", "content": "You are a friendly and knowledgeable AI assistant that can answer a variety of user questions and provide assistance."}]
            for session in user_info.get("U_session", []):
                if session["session_id"] == session_id:
                    if session["title"] == "新しい会話":
                        # 如果是新会话，标题用第一个content
                        if isinstance(contents, list) and contents:
                            session["title"] = contents[0]
                        else:
                            session["title"] = contents
                        current_app.container.upsert_item(user_info)
                    session_data = list(current_app.container_c.query_items(
                        query=f"SELECT * FROM user s WHERE s.session_id = '{session_id}'",
                        enable_cross_partition_query=True
                    ))
                    if session_data:
                        session_info = session_data[0]
                        history_data = session_info["S_info"]["content"]
                        try:
                            responses = []
                            # contents和file_contents都为list，逐一处理
                            if not isinstance(contents, list):
                                contents = [contents]
                            for idx, content in enumerate(contents):
                                file_content = file_contents[idx] if idx < len(file_contents) else ""
                                input_content = clue + content
                                input_content, response_ai = self.get_answer(file_content, input_content, dialogue_history, history_data)
                                history_data.append([input_content, response_ai])
                                responses.append({"response_ai": response_ai, "input": input_content})
                            session_info["S_info"] = {"content": history_data}
                            current_app.container_c.upsert_item(session_info)
                            logger.info(f"{username} input: {contents}")
                            return {
                                'session_info': {
                                    "responses": responses,
                                    "session_id": session_id
                                },
                                'code': 200,
                                'dialogue_history': dialogue_history
                            }
                        except Exception as e:
                            return {"message": str(e), "status": 404}
            return {"msg": "データ存在しない", "code": 404}
        else:
            raise messages.UserNotExistsError

    def delete(self):
        """セッションの削除"""
        args_parser = SessionParser()
        args = args_parser.parser.parse_args()
        username = args.get("username")
        session_id = args.get("session_id")
        if not username:
            raise messages.UserNameNotExistsError
        user_data = list(current_app.container.query_items(
            query=f"SELECT * FROM u WHERE u.username = '{username}'",
            enable_cross_partition_query=True
        ))
        if user_data:
            user_info = user_data[0]
            if session_id:
                sessions = user_info.get("U_session", [])
                updated_sessions = [session for session in sessions if session["session_id"] != session_id]
                user_info["U_session"] = updated_sessions
                current_app.container.upsert_item(user_info)

                history_data = list(current_app.container_c.query_items(
                    query=f"SELECT * FROM s WHERE s.session_id = '{session_id}'",
                    enable_cross_partition_query=True
                ))
                if history_data:
                    current_app.container_c.delete_item(session_id, partition_key=session_id)

                    logger.info(f"user: {username}\n option: Session deleted successfully")
                    return {'msg': 'success', 'code': 200}
            raise messages.SessionIdNotExistsError
        raise messages.UserNotExistsError

    @staticmethod
    def get_answer(input_file, input_data, question, history=None):
        if history:
            for data in history:
                history_message = {"role": "user", "content": data[0]}
                question.append(history_message)
        if input_file == "":
            message = {"role": "user", "content": input_data}
        else:
            prefix = input_file[0] + '\n\n' if input_file[0] else ''
            input_data = f"{prefix}{input_data}"
            if input_file[1]:
                message = {"role": "user", "content": [{"type": "text", "text": input_data}]}
                for base64_img in input_file[1]:
                    message["content"].append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_img}"}})
            else:
                message = {"role": "user", "content": input_data}
        question.append(message)
        if time.time() >= current_app.token_expires - 600:
            new_token = current_app.credential.get_token(os.getenv("SCOPE"))
            current_app.openai_token = new_token.token
            current_app.token_expires = new_token.expires_on
        current_app.openai.api_key = current_app.openai_token
        response = current_app.openai.ChatCompletion.create(
            deployment_id=current_app.deployment_id,  # Deploy Name
            messages=question,
            max_tokens=4000,
            temperature=0,
            seed=42 
        )
        answer = response['choices'][0]['message']['content'].strip()
        return input_data, answer

    @staticmethod
    def check_session(session_data):
        old_time = datetime.now() - timedelta(days=30)
        sessions = session_data.get("U_session", [])
        updated_sessions = []
        for session in sessions:
            create_time = session["create_time"]
            if datetime.fromisoformat(create_time) > old_time:
                updated_sessions.append(session)
        session_data["U_session"] = updated_sessions
        current_app.container.upsert_item(session_data)
        return session_data

    def read_txt(self, username, prompt_name):
        blob_client = current_app.container_client.get_blob_client(f"{username}/{prompt_name}")
        stream = blob_client.download_blob().readall()
        encoding = chardet.detect(stream)["encoding"]
        txt_content = stream.decode(encoding)
        return txt_content

    def check_name(self, prompt_name, username, attachment_names):
        if prompt_name:
            clue = self.read_txt(username, prompt_name)
        else:
            clue = ""
        file_contents = []
        if attachment_names:
            get_file_content = FileOperation()
            # Ensure attachment_names is a list
            if not isinstance(attachment_names, list):
                attachment_names = [attachment_names]
            for attachment_name in attachment_names:
                if attachment_name:
                    file_content = get_file_content(username, attachment_name)
                else:
                    file_content = ""
                file_contents.append(file_content)
        else:
            file_contents = [""]
        return clue, file_contents

    @staticmethod
    def detect_encoding(file_path):
        with open(file_path, "rb") as file:
            raw_data = file.read(10000)
            result = chardet.detect(raw_data)
            file.seek(0)
        return result["encoding"]


class FileManagement(GlobalResource):

    def post(self):
        """ファイルのアップロード"""
        args_parser = FileParser()
        args = args_parser.parser.parse_args()
        username = args.get("username")
        file = args.get("file")
        if not username:
            raise messages.UserNameNotExistsError
        if file and self.allowed_file(file.filename):
            try:
                blob_client = current_app.container_client.get_blob_client(f"{username}/{file.filename}")
                blob_client.upload_blob(file.stream, overwrite=True)

                logger.info(f"File '{file.filename}' uploaded successfully with description")
                return {
                    'message': f"File '{file.filename}' uploaded successfully with description",
                    'file_path': f"{username}/{file.filename}",
                    "code": 200
                }
            except Exception as e:
                return {'msg': f"Azure upload failed: {str(e)}", "code": 417}

        return {'msg': 'Invalid file type', "code": 400}

    def delete(self):
        args_parser = FileDelete()
        args = args_parser.parser.parse_args()
        username = args.get("username")
        filename = args.get("filename")
        if not username:
            raise messages.UserNameNotExistsError
        if filename:
            try:
                blob_client = current_app.container_client.get_blob_client(f"{username}/{filename}")
                blob_client.delete_blob()
                logger.info( f"user: {filename}\n option: File deleted successfully")
                return {"msg": f"{filename}ファイルの削除が成功しました", "code": 200}
            except Exception as e:
                return {"msg": f"{filename}ファイルが存在しないか、削除された", "code": 200}
        else:
            try:
                blobs_to_delete = list(current_app.container_client.list_blobs(name_starts_with=username))
                if blobs_to_delete:
                    current_app.container_client.delete_blobs(*[blob.name for blob in blobs_to_delete])
                    return {"msg": f"{filename}ファイルの削除が成功しました", "code": 200}
                else:
                    return {"msg": "ファイルが存在しないか、削除された", "code": 200}
            except Exception as e:
                return {"msg": str(e), "code": 200}
                # return {"msg": "ファイルが存在しないか、削除された", "code": 200}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


class Test1(Resource):

    def post(self):
        """ファイルのアップロード"""
        args_parser = FileParser()
        args = args_parser.parser.parse_args()
        username = args.get("username")
        file = args.get("file")
        if not username:
            raise messages.UserNameNotExistsError
        if file and self.allowed_file(file.filename):
            try:
                blob_client = current_app.container_client.get_blob_client(f"{username}/{file.filename}")
                blob_client.upload_blob(file.stream, overwrite=True)

                return {
                    'message': f"File '{file.filename}' uploaded successfully with description",
                    'file_path': f"{username}/{file.filename}",
                    "code": 200
                }
            except Exception as e:
                return {'msg': f"Azure upload failed: {str(e)}", "code": 417}

        return {'msg': 'Invalid file type', "code": 400}

    def delete(self):
        args_parser = FileDelete()
        args = args_parser.parser.parse_args()
        username = args.get("username")
        filename = args.get("filename")
        if not username:
            raise messages.UserNameNotExistsError
        if filename:
            try:
                blob_client = current_app.container_client.get_blob_client(f"{username}/{filename}")
                blob_client.delete_blob()
                return {"msg": f"{filename}ファイルの削除が成功しました", "code": 200}
            except Exception as e:
                return {"msg": f"{filename}ファイルが存在しないか、削除された", "code": 200}
        else:
            try:
                blobs_to_delete = list(current_app.container_client.list_blobs(name_starts_with=username))
                if blobs_to_delete:
                    current_app.container_client.delete_blobs(*[blob.name for blob in blobs_to_delete])
                    return {"msg": f"{filename}ファイルの削除が成功しました", "code": 200}
                else:
                    return {"msg": "ファイルが存在しないか、削除された", "code": 200}
            except Exception as e:
                return {"msg": str(e), "code": 200}
                # return {"msg": "ファイルが存在しないか、削除された", "code": 200}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


system_api.add_resource(SessionManagement, "/session_management")
system_api.add_resource(FileManagement, "/upload_file")
system_api.add_resource(Test1, "/test1")



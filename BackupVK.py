import requests
import json
import datetime
import sys
class VKBackup:
    def __init__(self, access_token, album, user_id, foto_stop, folder_foto):
        self.access_token = access_token
        self.album = album
        self.user_id = user_id
        self.foto_stop = foto_stop
        self.folder_foto = folder_foto
        self.version = '5.131'
        self.control_like = {}
        self.fileinfo = []

    def get_photos(self):
        params = {
            'access_token': self.access_token,
            'v': self.version,
            'owner_id': self.user_id,
            'album_id': self.album,
            'extended': 1
        }
        url = 'https://api.vk.com/method/photos.get'
        response = requests.get(url, params=params)
        return response.json()

    def backup_photos(self):
        print("Получаю список файлов и задаю маску имени")
        try:
            for my_photo in self.get_photos()["response"]["items"]:
                if self.foto_stop != 0:
                    if my_photo["likes"]["count"] not in self.control_like.keys():
                        self.control_like[my_photo["likes"]["count"]] = my_photo["sizes"][-1]["url"]
                        filename = f"{my_photo["likes"]["count"]}.jpg"
                        size = my_photo["sizes"][-1]["type"]
                    else:
                        self.control_like[
                            (f"{my_photo["likes"]["count"]} "
                             f"{datetime.datetime.fromtimestamp(my_photo["date"]).strftime('%d-%m-%Y')}")] = (
                            my_photo)["sizes"][-1]["url"]
                        filename = (f"{my_photo["likes"]["count"]} "
                                    f"{datetime.datetime.fromtimestamp(my_photo["date"]).strftime('%d-%m-%Y')}.jpg")
                        size = my_photo["sizes"][-1]["type"]

                    self.fileinfo.append({"filename": filename, "size": size})
                    self.foto_stop -= 1

                else:
                    break
        except KeyError:
            print(f"Произошла ошибка доступа к пользователю ID № {self.user_id} VK! Либо ошибка Токена!")
            return

        print("Пытаюсь создать папку для полученных фото")
        params = {'path': self.folder_foto}
        headers = {'Authorization': token_disk}
        response = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                                params=params,
                                headers=headers)
        print("Статус создания Папки", response.status_code)

        print("Приступаю к загрузке фото")
        for likes_count, url_foto in self.control_like.items():
            url_foto = url_foto.replace("&", "%26")
            file_name = f"{likes_count}.jpg"
            params = {'path': f"{self.folder_foto}/{file_name}"}
            payload = ""
            response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload?url=' + url_foto,
                                     params=params,
                                     headers=headers,
                                     data=payload)
            print("Загрузка фото:", file_name, "Статус", response.status_code)

        print("Сохраняю json с технической информацией.")
        with open('filefoto.json', 'w') as jf:
            json.dump(self.fileinfo, jf)

# Чтение ключей из файла
try:
    with open('token.txt', "r", encoding="utf8") as f:
        access_token = f.readline().strip()
        token_disk = f.readline().strip()
        print('Считал данные для доступов')
except FileNotFoundError:
    print("Не найден файл с ключами доступа")
    sys.exit()

# vk_backup = VKBackup(access_token, 'profile', 'НОМЕР ID', 12, "FOTOS")

"""Если нужно с вводом"""
vk_backup = VKBackup(access_token,
                     'profile',
                     input('Укажите номер ID VK пользователя: '),
                     5,
                     "FOTOS")
vk_backup.backup_photos()

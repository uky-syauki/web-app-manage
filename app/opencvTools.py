import cv2 as cv
import numpy as np
import base64
import os
from PIL import Image
from app import db
from app.models import User

class OPENCV:
    def __init__(self):
        self.face_cascade = cv.CascadeClassifier('cascade/face_detect.xml')
        self.eye_cascade = cv.CascadeClassifier('cascade/eye_detect.xml')
        self.recognition = cv.face.LBPHFaceRecognizer_create()
        self.path_dataset = 'dataset/'
        self.path_latih = 'training/latih.yml'
        self.path_sampleimg = 'sampleimg/'
    def set_path(self):
        if not os.path.exists(self.path_dataset):
            os.mkdir(self.path_dataset)
        if not os.path.exists(self.path_latih):
            os.mkdir(self.path_latih)
        if not os.path.exists(self.path_sampleimg):
            os.mkdir(self.path_sampleimg)
    def set_path_sampleimg_user(self, name):
        self.set_path()
        if not os.path.exists(self.path_sampleimg):
            os.mkdir(self.path_sampleimg)
        if not os.path.exists(self.path_sampleimg+name):
            os.mkdir(self.path_sampleimg+name)
    def add_sampleimg(self, user ,foto):
        try:
            self.set_path_sampleimg_user(user.username)
            jumlah = len(os.listdir(self.path_sampleimg+user.username)) + 1
            image = foto.split(',')[1]
            image_bin = image.encode('utf-8')
            image_np = np.frombuffer(base64.b64decode(image_bin), dtype=np.uint8)
            img = cv.imdecode(image_np, cv.IMREAD_COLOR)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            wajah = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            counter = 0
            for (x, y, w, h) in wajah:
                if counter == 0:
                    counter += 1
                mata = self.eye_cascade.detectMultiScale(gray[y:y+h, x:x+w], scaleFactor=1.3, minNeighbors=5)
                for (x2, y2, w2, h2) in mata:
                    if counter == 2:
                        if jumlah <= 15:
                            fnama = f"{self.path_sampleimg}{user.username}/{user.username}.{user.id}.{jumlah}.jpg"
                            cv.imwrite(fnama, img)
                    counter += 1
            print(f"[INFO] > Menyimpan {fnama}")
        except:
            print("[INFO] > Gagal Menyimpan")
    def set_dataset(self, user):
        path = self.path_sampleimg+user.username
        daftar_sampleimg = os.listdir(path)
        # jumlah = 0
        if len(daftar_sampleimg) > 0:
            for isi in daftar_sampleimg:
                counter = 0
                img = cv.imread(f'{path}/{isi}')
                gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                wajah = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
                for (x, y, w, h) in wajah:
                    if counter == 0:
                        counter += 1
                    mata = self.eye_cascade.detectMultiScale(gray[y:y+h, x:x+w], scaleFactor=1.3, minNeighbors=5)
                    for (x2, y2, w2, h2) in mata:
                        if counter > 0:
                            counter += 1
                        if counter == 2:
                            # jumlah += 1
                            cv.imwrite(f'{self.path_dataset}{isi}', gray[y:y+h, x:x+w])
                # counter = 0
        self.latih_dataset()
    def latih_dataset(self):
        print('[INFO]: Start training mohon tunggu')
        list_image = os.listdir(self.path_dataset)
        sample_wajah = []
        ids = []
        for isi in list_image:
            PILimage = Image.open(self.path_dataset+isi).convert('L')
            img_numpy = np.array(PILimage, 'uint8')
            id = int(os.path.split(isi)[-1].split(".")[1])
            sample_wajah.append(img_numpy)
            ids.append(id)

        self.recognition.train(sample_wajah, np.array(ids))
        self.recognition.write(self.path_latih)
        print('[INFO]: Latih dataset selesai..')
    def deteksi_wajah(self, path_image, alluser):
        self.recognition.read(self.path_latih)
        id = 0
        names = ['None'] + alluser
        prediksi = 100
        try:
            img = path_image.split(',')[1]
            img_bin = img.encode('utf-8')
            img_np = np.frombuffer(base64.b64decode(img_bin), dtype=np.uint8)
            img = cv.imdecode(img_np, cv.IMREAD_COLOR)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            cv.imwrite('sampleimg/tes/1.jpg', gray)
            wajah = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            for (x, y, w, h) in wajah:
                id, prediksi = self.recognition.predict(gray[y:y+h, x:x+w])
                id = names[id]
                prediksi = (100 - round(prediksi))
        except:
            id = 'None'
            prediksi = 0
        # if prediksi < 40:
        #     prediksi = 0
        #     id = "Tidak Kenal"
        return [id, prediksi]
    def deteksi_wajah_img(self, path_image, alluser):
        self.recognition.read(self.path_latih)
        id = 0
        names = ['None'] + alluser
        prediksi = 100
        try:
            img = cv.imread(path_image)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            cv.imwrite('sampleimg/tes/1.jpg', gray)
            wajah = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            for (x, y, w, h) in wajah:
                id, prediksi = self.recognition.predict(gray[y:y+h, x:x+w])
                id = names[id]
                prediksi = (100 - round(prediksi))
        except:
            id = 'None'
            prediksi = 0
        # if prediksi < 40:
        #     prediksi = 0
        #     id = "Tidak Kenal"
        return [id, prediksi]
    def seleksi_sampleimg(self, user, allUser):
        sampleimg_user_path = self.path_sampleimg+user.username
        list_sampleimg_user = os.listdir(sampleimg_user_path)
        hstatc = []
        for isi in list_sampleimg_user:
            dapat = self.deteksi_wajah_img(sampleimg_user_path + '/' + isi, allUser)
            if dapat[1] < 80:
                os.remove(sampleimg_user_path+'/'+isi)
            hstatc.append([dapat[0], dapat[1], sampleimg_user_path + isi])
        self.set_dataset(user)
        return hstatc
    def renameSampleimg(self,user):
        lsdir = os.listdir(self.path_sampleimg+user.username)
        hitung = 1
        for isi in lsdir:
            os.rename(self.path_sampleimg+user.username+isi, self.path_sampleimg+user.username+'/'+user.username+'.'+user.id+hitung+'.jpg')
    def jumlah_sampleimg_user(self,user):
        return len(os.listdir((self.path_sampleimg+user.username)))
import customtkinter
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import tkintermapview
from tkintermapview import TkinterMapView
import pandas as pd
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import utils
from tkinter import filedialog
import geocoder

import os 
import sys

#Modul untuk Time Zone
import datetime
import timezonefinder, pytz

#Modul untuk Ketinggian
import json
import urllib.request

#Modul Kalender
import calendar
import math

#Tema tkinter
customtkinter.set_default_color_theme("blue")

WIDTH = 1155
HEIGHT = 650

def change_appearance_mode(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)

def set_button_highlight(button):
    # Reset semua tombol ke tampilan awal
    for btn in all_buttons:
        btn.configure(fg_color='#3B8ED0')
    
    # Set tombol yang dipilih ke tampilan khusus
    button.configure(fg_color='#CD3B3B')

def clear_marker_event():
    set_button_highlight(button_about)

#Menentukan Ketinggian(Elevation)
def ketinggian(latitude, longitude, api_url="https://api.open-elevation.com/api/v1/lookup"):
    #Membuat data untuk lokasi
    data_lokasi = {"locations": [{"latitude": latitude, "longitude": longitude}]}
    data_json = json.dumps(data_lokasi).encode('utf8')

    #Mengirim permintaan ke API
    respon = urllib.request.Request(api_url, data_json, headers={'Content-Type': 'application/json'})
    fp = urllib.request.urlopen(respon) 

    #Respon
    res_byte = fp.read()
    res_str = res_byte.decode("utf8")
    js_str = json.loads(res_str)
    fp.close()    

    #Periksa Hasil
    if 'results' in js_str and len(js_str['results']) > 0:
        ketinggian_dari_permukaan_laut = js_str['results'][0]['elevation']
        return ketinggian_dari_permukaan_laut
    else:
        return None   

def conv_bulan_grego_to_angka(x):
    month_mapping = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
    }
    selected_month = month_mapping.get(x)
    return selected_month

def conv_angka_to_bulan_grego(x):
    month_mapping = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
    }        
    selected_month = month_mapping.get(x)
    return selected_month

def conv_angka_to_bulan_hijri(x):
    month_mapping = {
    1: "Muharram",
    2: "Safar",
    3: "Rabiul Awal",
    4: "Rabiul Akhir",
    5: "Jumadil Awal",
    6: "Jumadil Akhir",
    7: "Rajab",
    8: "Sya'ban",
    9: "Ramadhan",
    10: "Syawal",
    11: "Dzulkaidah",
    12: "Dzulhijjah",
    }        
    selected_month = month_mapping.get(x)
    return selected_month

def conv_bulan_hijri_to_angka(x):
    month_mapping = {
    "Muharram": 1,
    "Shafar": 2,
    "Rabiul Awal": 3,
    "Rabiul Akhir": 4,
    "Jumadil Awal": 5,
    "Jumadil Akhir": 6,
    "Rajab": 7,
    "Sya'ban": 8,
    "Ramadhan": 9,
    "Syawal": 10,
    "Dzulkaidah": 11,
    "Dzulhijjah": 12,
    }
    selected_month = month_mapping.get(x)
    return selected_month

def gregorian_to_hijri(tahun, bulan, hari, zona, jam, menit):
    def syarat(bulan, tahun):
        if bulan <=2:
            bulan = bulan + 12
            tahun = tahun - 1
        else:
            bulan = bulan
            tahun = tahun
        return bulan, tahun
    bln, thn = syarat(bulan, tahun)
            
    def gregorian():
        B = bln - 4
        C = math.floor(int(thn)/100)
        D = math.floor(C/4)
        E = math.floor(int(thn)/4)
        F = (E-(C-D))
        G = int(thn) - F
        I = (jam + menit/60)/24
        JD1 = 1721149.5 + 366*F + 365*G +math.floor(30.6001*B) + hari + I
        JD = 1721149.5 + 366*F + 365*G +math.floor(30.6001*B) + hari + I - zona/24
        return JD1, JD
    JulianDayGMT, JulianDay = gregorian()

    def hijriah():
        delta_JDX = JulianDay -1948438.5
        JDX = 30*(delta_JDX//10631)
        K = delta_JDX % 10631
        L = K // 354
        def hitung_hasil(x):
            hasil = 0
            for i in range(1, math.floor(x) + 1):
                if i in [2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29]:
                    hasil += 355
                else:
                    hasil += 354
            return hasil
        N = hitung_hasil(L)
        O = K - N
        P = math.floor(O)
        Q = math.floor(P/29.5)
        R = Q + 1
        def hitung_sisahari(Q):
            sisahari = 0
            for i in range(1, math.floor(Q) + 1):
                if i in [1, 3, 5, 7, 8, 9, 11]:
                    sisahari += 30
                else:
                    sisahari += 29
            return sisahari
        SISAHARI = hitung_sisahari(Q)
        S = O - SISAHARI + zona/24
        HARI_HIJRI = math.floor(S)
        BULAN_HIJRI = R
        TH_HIJRI = math.floor(JDX + L + 1)

        #Cari sisa jam
        U = S - HARI_HIJRI
        V = math.floor(U*24)
        #cari sisa menit
        W = math.floor(((U)*24-V)*60) 

        #Atasi hari hijri yang tanggalnya 0
        if HARI_HIJRI <= 0 :
            i = BULAN_HIJRI
            if i in [2, 4, 6, 8, 10, 12]:
                HARI_HIJRI = 30 + HARI_HIJRI
                BULAN_HIJRI = BULAN_HIJRI - 1
            else:
                HARI_HIJRI = 29 + HARI_HIJRI
                BULAN_HIJRI = BULAN_HIJRI - 1                

        return HARI_HIJRI, BULAN_HIJRI, TH_HIJRI, V, W
    h_hijri, b_hijri, Tt_hijri, jam_hijri, menit_hijri = hijriah()
    return h_hijri, b_hijri, Tt_hijri, JulianDay, JulianDayGMT, jam_hijri, menit_hijri

def hijri_to_grego(tahun, bulan, hari, zona, jam, menit):
    #Pendefinisian Konversi Hijriyah ke JD
    def hij_to_JD():
        YYYY = tahun
        MM = bulan
        DD = hari
        #Tahun yang telah dilalui adalah YYYY - 1
        AB = YYYY - 1

        #Bagi tahun dengan 30
        BC = AB // 30           #Ini menghasilkan banyaknya bilangan bulat kelipatan 30 tahun dari YYYY-1 tahun
        CD = AB % 30            #Ini menghasilkan sisa tahun setelah kelipatan BC tersebut

        #Jumlah hari dalam kelipatan 30 tahun bulan hijriyah adalah 10631 hari
        DE = BC * 10631         #Ini menghasilkan banyaknya hari dalam kelipatan BC

        #Sebenarnya dalam CD tahun sisa tersebut ada kemungkinan merupakan tahun kabisat, sehingga kita perlu mengoreksinya
        def hitung_hasil(x):
            hasil = 0
            for i in range(1, math.floor(x) + 1):
                #Ketika tahun kabisat maka kita menjumlahkan hasil dengan 355, selain itu kita jumlahkan dengan 354
                if i in [2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29]:
                    hasil += 355
                else:
                    hasil += 354
            return hasil

        #Jumlah Hari dalam CD Tahun (Sisa tahun)
        EF = hitung_hasil(CD)

        #Bulan yang telah selesai dilalui pada MM adalah MM - 1
        GH = MM - 1             #Ini akan menghasilkan banyak bulan dengan maksimal 11 bulan
                          #Maka kita tidak perlu melihat apakah tahun itu kabisat atau tidak

        def hitung_hasil1(y):
            hasil1 = 0
            for i in range(1, math.floor(y) + 1):
                #Ketika bulan ganjil, maka hari dijumlah 30
                if i in [1, 3, 5, 7, 9, 11]:
                    hasil1 += 30
                else:
                    hasil1 += 29
            return hasil1

        #Banyak hari dalam GH bulan yang telah dilalui
        HI = hitung_hasil1(GH)

        waktu = (jam + menit/60)*24
        #Hasil perhitungan semua hari dijumlahkan dengan tanggal pada waktu itu
        IJ = DE + EF + HI + DD + waktu         #Ini menghasilkan total hari yang telah dilalui dengan acuan awal ditetapkannya kalender hijriyah

        #Nilai JD merupakan hasil penjumlahan IJ dengan Delta JD nol = 1948438.5
        JD = 1948438.5 + IJ
        
        JD1 = JD - zona/24

        return JD, JD1

    JulianDayGMT, JulianDay = hij_to_JD()

    def jd_gregorian(Hasil_JD_Y):

        #Kita gunakan acuan awal tahun adalah 31 Maret Tahun 0 dengan JD 1721149.5
        #Kita dapat mencari banyaknya hari yang telah dilalui terhadap titik tersebut
        D_JD = Hasil_JD_Y - 1721149.5

        #Dalam 400 tahun gregorian, terdapat 97 tahun kabisat, sehingga jumlah hari tiap 400 tahun adalah 146097 hari
        KL = math.floor(D_JD/146097)              #Ini menghasilkan banyak kelipatan 400 pada tahun yang ada

        LM = 146097 * KL                          #Ini menghasilkan jumlah hari yang telah ditempuh

        MN = D_JD - LM                            #Ini menghasilkan sisa hari yang ada

        #MN akan menghasilkan maksimal 399 tahun
        #Kita dapat membagi hari sisa dalam kelipatan 100 tahun
        #Dalam 100 tahun, tedapat 24 tahun kabisat, jumlah harinya adalah 36524
        NO = math.floor(MN/36524)                 #Ini menghasilkan banyak kelipatan 100 pada tahun sisa yang ada

        OP = NO * 36524                           #Ini menghasilkan jumlah hari dalam kelipatan NO

        #Sisa hari sekarang menjadi:
        PQ = MN - OP

        #PQ akan menghasilkan tahun dengan jumlah paling maksimal 99 tahun
        #Kita dapat membagi hari sisa dalam kelipatan 4 tahun
        #Dalam 4 tahun, terdapat 1 tahun kabisat, jumlah harinya adalah 1461
        QR = math.floor(PQ/1461)                  #Ini menghasilkan banyak kelipatan 4 pada tahun sisa yang ada

        RS = QR * 1461                            #Ini menghasilkan jumlah hari dalam kelipatan QR

        #Sisa hari menjadi:
        ST = PQ - RS

        #ST hari akan menghasilkan maksimal 3 tahun yang telah berjalan
        #Dalam 3 tahun tidak ada tahun kabisat, kita dapat membaginya dengan 365
        TU = math.floor(ST/365)                   #Ini menghasilkan banyak tahun sisa

        UV = TU * 365                             #Ini menghasilkan Jumlah hari dalam TU tahun sisa

        #Sisa hari menjadi:
        VW = ST - UV

        #VW hari akan menghasilkan maksimal 11 bulan yang telah dilewati
        #Kita gunakan acuan bulan pertama adalah Maret
        WX = math.floor(VW/30)               #Ini menghasilkan jumlah bulan yang telah selesai dilalui

        #Jumlah hari dalam WX dalam acuan bulan maret
        def syarat_bulan(b):
            hasilbulan = 0
            for i in range(1, math.floor(b) + 1):
                if i in [1, 3 , 5, 6, 8, 10, 11]:
                    hasilbulan += 31
                else:
                    hasilbulan += 30
            return hasilbulan

        XY = syarat_bulan(WX)                     #Ini menghasilkan jumlah hari dalam WX bulan

        #Sisa hari menjadi yang telah dilalui adalah: VW - XY sedangkan tanggal gregorian saat ini dijumlahkan 1
        YZ = VW - XY + 1 + zona/24

        #YZ merupakan jumlah hari sisa, ini masih dapat berupa bilangan pecahan
        ZY = math.floor(YZ)                      #Ini merupakan Tanggal Gregorian
        
        jam_grego = math.floor((YZ-ZY)*24)
        menit_grego = math.floor(((YZ-ZY)*24-jam_grego)*60)
        
        #Kasus ketika hari sisa = 0
        if ZY <= 0:
            i = WX
            if i in [1, 3 , 5, 6, 8, 10, 11]:
                ZY = 30 + ZY
                WX = WX - 1
            else:
                ZY = 31 + ZY
                WX = WX -1

        #Tahun yang dihasilkan:
        TTTT = KL*400 + NO*100 + QR*4 + TU

        #Karena menggunakan acuan bulan Maret, maka bulan Januari dan Februari merupakan bulan ke 13 dan 14 pada tahun sebelumnya
        #Bulan pada tahun gregorian adalah (WX+1)+3
        BB = WX + 4
        def syaratbulan(BB, TTTT):
            if BB > 12:
                BB = BB - 12
                TTTT = TTTT +1
            else:
                BB = BB
                TTTT = TTTT
            return BB, TTTT
  
        hasil_BB, hasil_TTTT = syaratbulan(BB, TTTT)
        #Hasil_BB ini adalah Bulan pada Gregorian
        #Hasil_TTTT ini adalah tahun pada Gregorian

        return ZY, hasil_BB, hasil_TTTT, jam_grego, menit_grego

    h_grego, b_grego, Tt_grego, jam_grego, menit_grego = jd_gregorian(JulianDay)
    return h_grego, b_grego, Tt_grego, JulianDay, JulianDayGMT, jam_grego, menit_grego


def hitung_waktu_sholat(Julian_Day, bujur, lintang, ketinggian, zona, subuhdegree, isyadegree, asharshadow, correction, imsaktime, duhatime):
    #Menghitung Waktu Sholat
    def perhitungan1():
        T = 2*math.pi*(Julian_Day - 2451545)/365.25
        Delta = 0.37877 + 23.264*math.sin(math.radians(57.297*T-79.547)) + 0.3812*math.sin(math.radians(2*57.297*T-82.682)) + 0.17132*math.sin(math.radians(3*57.297*T-59.722))

        U = (Julian_Day - 2451545)/36525
        L0 = 280.46607 + 36000.7698*U
        L0rad = math.radians(L0)
        ET = (-(1789+237*U)*math.sin(L0rad)-(7146-62*U)*math.cos(L0rad)+(9934-14*U)*math.sin(2*L0rad)-(29+5*U)*math.cos(2*L0rad)+(74+10*U)*math.sin(3*L0rad)+(320-4*U)*math.cos(3*L0rad)-212*math.sin(4*L0rad))/1000

        WTransit = 12 + zona - bujur/15 - ET/60
        KA = int(asharshadow)
        x = KA + math.tan(abs(math.radians(Delta - lintang)))
        Altitude_Ashar = math.degrees(math.atan(1/x))
        Altitude_Magrib = -0.8333 - 0.0347*((ketinggian)**(1/2))
        Altitude_Isya = int(isyadegree)
        Altitude_Subuh = int(subuhdegree)
        Altitude_Terbit = -0.8333 - 0.0347*((ketinggian)**(1/2))
        return Delta, WTransit, Altitude_Ashar, Altitude_Magrib, Altitude_Isya, Altitude_Subuh, Altitude_Terbit

    Delta, WTransit, Altitude_Ashar, Altitude_Magrib, Altitude_Isya, Altitude_Subuh, Altitude_Terbit = perhitungan1()

    def HourAngle(Alt):
        HA = ((math.sin(math.radians(Alt))-math.sin(math.radians(lintang))*math.sin(math.radians(Delta)))/(math.cos(math.radians(lintang))*math.cos(math.radians(Delta))))
        HAngle = math.acos(HA)
        return HAngle

    HA_Ashar = HourAngle(Altitude_Ashar)
    HA_Magrib = HourAngle(Altitude_Magrib)
    HA_Isya = HourAngle(Altitude_Isya)
    HA_Subuh = HourAngle(Altitude_Subuh)
    HA_Terbit = HourAngle(Altitude_Terbit)

    def waktu_sholat():
        Dzuhur = WTransit + int(correction)/60
        Ashar = WTransit + math.degrees(HA_Ashar)/15 + int(correction)/60
        Magrib = WTransit + math.degrees(HA_Magrib)/15 + int(correction)/60
        Isya = WTransit + math.degrees(HA_Isya)/15 + int(correction)/60
        Subuh = WTransit - math.degrees(HA_Subuh)/15 +int(correction)/60
        Terbit = WTransit - math.degrees(HA_Terbit)/15
        return Dzuhur, Ashar, Magrib, Isya, Subuh, Terbit

    Dzuhur, Ashar, Magrib, Isya, Subuh, Terbit = waktu_sholat()

    def convertJam(x):
        Jam = math.floor(x)
        B =  x - Jam
        Menit = str(int(B*60)).zfill(2)
        Detik = (B-math.floor(x-Jam))*60
        if Detik <= 1:
           Menit = str(int(B*60)+1).zfill(2) 
        JAMX = str(Jam).zfill(2)
        return JAMX, Menit
 
    JamDzuhur, MenitDzuhur = convertJam(Dzuhur)
    JamAshar, MenitAshar, = convertJam(Ashar)
    JamMaghrib, MenitMaghrib = convertJam(Magrib)
    JamIsya, MenitIsya = convertJam(Isya)
    JamSubuh, MenitSubuh = convertJam(Subuh)
    JamTerbit, MenitTerbit = convertJam(Terbit)

    #Duha
    def Duha():
        Duhamenit = int(int(MenitTerbit) + int(duhatime) + int(correction))
        Duhajam = int(JamTerbit)
        if Duhamenit > 60:
            Duhamenit = Duhamenit - 60
            Duhajam = Duhajam + 1
        return Duhajam, Duhamenit
    Duhajam, Duhamenit = Duha()
    JamDuha, MenitDuha = str(Duhajam).zfill(2), str(Duhamenit).zfill(2)
    
    #Imsak
    def Imsak():
        Imsakmenit = (int(MenitSubuh) + int(imsaktime))
        Imsakjam = int(JamSubuh)
        if Imsakmenit < 0:
            Imsakmenit = Imsakmenit + 60
            Imsakjam = Imsakjam - 1
        return Imsakjam, Imsakmenit
        
    Imsakjam, Imsakmenit = Imsak()
    JamImsak, MenitImsak = str(Imsakjam).zfill(2), str(Imsakmenit).zfill(2)
    return JamDzuhur, MenitDzuhur, JamAshar, MenitAshar, JamMaghrib, MenitMaghrib, JamIsya, MenitIsya, JamSubuh, MenitSubuh, JamTerbit, MenitTerbit, JamImsak, MenitImsak, JamDuha, MenitDuha
    
def apakah_hari_ini(x, y):
    #Hitung hari tersebut
    hari_sekarang = int((x + y/24 - 1721425.5)%7)
    hari_mapping = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
    }        
    selected_hari = hari_mapping.get(hari_sekarang)
    return selected_hari

def weton_hari_ini(x,y):
    #Acuan 27 November 2023 sebagai pahing
    hari_jawa = ((x + y/24 - 2460275.5)%5)
    hari_mapping = {
    0: "Pahing",
    1: "Pon",
    2: "Wage",
    3: "Kliwon",
    4: "Legi",
    }        
    selected_harijawa = hari_mapping.get(hari_jawa)
    return selected_harijawa

def hitung_jumlah_hari_bulan_grego(selected_year, selected_month):
    # Menghitung jumlah hari dalam bulan yang dipilih
    days_in_month = calendar.monthrange(int(selected_year), selected_month)[1]

    # Membuat daftar nilai (values) untuk tanggal_menu
    date_values = [str(day) for day in range(1, days_in_month + 1)]
    return date_values

def hitung_jumlah_hari_bulan_hijri(selected_year, selected_month):
    #Convert Hijri date to Gregorian date
    h_grego, b_grego, Tt_grego, JulianDay, JulianDayGMT, jam_grego, menit_grego = hijri_to_grego(selected_year, selected_month, 1, 0, 0, 0)

    #Calculate the next Hijri month
    next_month = selected_month + 1 if selected_month < 12 else 1
    next_year = selected_year + 1 if selected_month == 12 else selected_year
    
    #Convert the first day of the next Hijri month to Gregorian date
    h_grego1, b_grego1, Tt_grego1, JulianDay1, JulianDayGMT1, jam_grego1, menit_grego1 = hijri_to_grego(next_year, next_month, 1, 0, 0, 0)

    # Calculate the difference in days between the current and next Gregorian dates
    days_in_month = int(JulianDay1 - JulianDay)
    date_values = [str(day) for day in range(1, days_in_month + 1)]
    return date_values
        
def tombol_waktusholat():
    for widget in frame_right.winfo_children():
        widget.destroy()
    set_button_highlight(button_waktusholat)
    # List untuk menyimpan marker
    marker_list = []

    def set_marker_event(coords):
        for marker in marker_list:
            marker.delete()
        marker_list.append(map_widget.set_marker(coords[0], coords[1]))

        #Input Entry Lat dan Lng
        entry2.configure(state='normal')
        entry2.delete(0, 'end')
        entry2.insert(0, str(coords[0]))  # Latitude
        entry2.configure(state='disabled')
        entry3.configure(state='normal')
        entry3.delete(0, 'end')
        entry3.insert(0, str(coords[1]))  # Longitude  
        entry3.configure(state='disabled') 

        #Mencari Nilai Time Zone
        tf = timezonefinder.TimezoneFinder()
        #Mendapatkan nama zona waktu sesuai database pada pytz
        timezone_str = tf.certain_timezone_at(lat=coords[0], lng=coords[1])
        if timezone_str is None:
            entry4.delete(0, 'end')
            entry4.insert(0, '0')
        else:
            timezone = pytz.timezone(timezone_str)
            utc_offset_hours = timezone.utcoffset(datetime.datetime.utcnow()).total_seconds()/3600
            entry4.delete(0, 'end')
            entry4.insert(0, (utc_offset_hours))            
        
        #Melakukan penentuan ketinggian
        heigh = ketinggian(coords[0], coords[1])
        if heigh is not None:
            entry5.delete(0, 'end')
            entry5.insert(0, heigh)
        else:
            entry4.delete(0, 'end')
            entry4.insert(0, '0')         

    def clear_marker_event():
        for marker in marker_list:
            marker.delete()
        entry.configure(state='normal')
        entry.delete(0, 'end')      
        entry.configure(placeholder_text="type address")
        entry2.configure(state='normal')
        entry2.delete(0, 'end')    
        entry2.configure(placeholder_text="Latitude")
        entry2.configure(state='disabled')
        entry3.configure(state='normal')
        entry3.delete(0, 'end')      
        entry3.configure(placeholder_text="Longitude")
        entry3.configure(state='disabled')
        entry4.configure(state='normal')
        entry4.delete(0, 'end')      
        entry4.configure(placeholder_text="Time Zone")
        entry5.configure(state='normal')
        entry5.delete(0, 'end')      
        entry5.configure(placeholder_text="Elevation")
        cek_varloc.set(False)

    def search_event(event=None):
        map_widget.set_address(entry.get())
        for marker in marker_list:
            marker.delete()
        x, y = tkintermapview.convert_address_to_coordinates(entry.get())
        marker_list.append(map_widget.set_marker(x, y))
        
        #Input Entry Lat dan Lng
        entry2.configure(state='normal')
        entry2.delete(0, 'end')
        entry2.insert(0, str(x))  # Latitude
        entry2.configure(state='disabled')
        entry3.configure(state='normal')
        entry3.delete(0, 'end')
        entry3.insert(0, str(y))  # Longitude  
        entry3.configure(state='disabled') 

        #Mencari Nilai Time Zone
        tf = timezonefinder.TimezoneFinder()
        #Mendapatkan nama zona waktu sesuai database pada pytz
        timezone_str = tf.certain_timezone_at(lat=x, lng=y)
        if timezone_str is None:
            entry4.delete(0, 'end')
            entry4.insert(0, '0')
        else:
            timezone = pytz.timezone(timezone_str)
            utc_offset_hours = timezone.utcoffset(datetime.datetime.utcnow()).total_seconds()/3600
            entry4.delete(0, 'end')
            entry4.insert(0, (utc_offset_hours))            
        
        #Melakukan penentuan ketinggian
        heigh = ketinggian(x, y)
        if heigh is not None:
            entry5.delete(0, 'end')
            entry5.insert(0, heigh)
        else:
            entry4.delete(0, 'end')
            entry4.insert(0, '0')  

    def change_map(new_map: str):
        if new_map == "OpenStreetMap":
            map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "GoogleMap":
            map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "GoogleSatellite":
            map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    #Label add location
    label_location = customtkinter.CTkLabel(frame_right, text="Add Location:    (Right Click to edit and add Marker)", anchor="w")
    label_location.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky='wn')

    # Kotak teks untuk pencarian alamat
    entry = customtkinter.CTkEntry(master=frame_right, placeholder_text="type address")
    entry.grid(row=1, column=0, sticky="we", padx=(12, 0), pady=0)
    entry.bind("<Return>", search_event)
    
    def cek_location():
        if cek_varloc.get():
            g = geocoder.ip('me')
            x, y = g.latlng
            currentlocation = tkintermapview.convert_coordinates_to_address(x, y)
            entry.configure(state='normal')
            entry.delete(0, 'end')
            entry.insert(0, (f"{currentlocation.city}, {currentlocation.state}, {currentlocation.country}")) 
            map_widget.set_position(x, y)
            entry.configure(state='disabled')
            for marker in marker_list:
                marker.delete()
            marker_list.append(map_widget.set_marker(x, y))

            #Input Entry Lat dan Lng
            entry2.configure(state='normal')
            entry2.delete(0, 'end')
            entry2.insert(0, str(x))  # Latitude
            entry2.configure(state='disabled')
            entry3.configure(state='normal')
            entry3.delete(0, 'end')
            entry3.insert(0, str(y))  # Longitude  
            entry3.configure(state='disabled') 

            #Mencari Nilai Time Zone
            tf = timezonefinder.TimezoneFinder()
            #Mendapatkan nama zona waktu sesuai database pada pytz
            timezone_str = tf.certain_timezone_at(lat=x, lng=y)
            if timezone_str is None:
                entry4.delete(0, 'end')
                entry4.insert(0, '0')
            else:
                timezone = pytz.timezone(timezone_str)
                utc_offset_hours = timezone.utcoffset(datetime.datetime.utcnow()).total_seconds()/3600
                entry4.delete(0, 'end')
                entry4.insert(0, (utc_offset_hours))            
        
            #Melakukan penentuan ketinggian
            heigh = ketinggian(x, y)
            if heigh is not None:
                entry5.delete(0, 'end')
                entry5.insert(0, heigh)
            else:
                entry4.delete(0, 'end')
                entry4.insert(0, '0')  

        else:
            entry.configure(state='normal')
            entry.delete(0, 'end')      
            entry.configure(placeholder_text="type address")
            entry2.configure(state='normal')
            entry2.delete(0, 'end')    
            entry2.configure(placeholder_text="Latitude")
            entry2.configure(state='disabled')
            entry3.configure(state='normal')
            entry3.delete(0, 'end')      
            entry3.configure(placeholder_text="Longitude")
            entry3.configure(state='disabled')
            entry4.configure(state='normal')
            entry4.delete(0, 'end')      
            entry4.configure(placeholder_text="Time Zone")
            entry5.configure(state='normal')
            entry5.delete(0, 'end')      
            entry5.configure(placeholder_text="Elevation")
            for marker in marker_list:
                marker.delete()     

    cek_varloc = tk.BooleanVar()
    checkboxloc = tk.Checkbutton(master=frame_right, text='Current Location with IP', variable=cek_varloc, command=cek_location)
    checkboxloc.grid(row=0, column=1, padx=(0, 0), pady=(12,12), sticky='wn')
    
    #Tombol "Search"
    button_5 = customtkinter.CTkButton(master=frame_right, text="Search", width=90, command=search_event)
    button_5.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=0)

    # Widget peta
    map_widget = TkinterMapView(frame_right, corner_radius=0)
    map_widget.grid(row=2, column=0, columnspan=2, sticky="nswe", padx=(10, 10), pady=(10, 10))

    # Pilihan Model Map
    map_label = customtkinter.CTkLabel(frame_right, text="Maps Mode:", anchor="w")
    map_label.grid(row=0, column=2, padx=(12, 0), pady=(10, 0), sticky='wn')
    map_option_menu = customtkinter.CTkOptionMenu(frame_right, values=["OpenStreetMap", "GoogleMap", "GoogleSatellite"],
                                               command=change_map)
    map_option_menu.grid(row=1, column=2, sticky="we", padx=(12, 12), pady=0)
    
    #Frame Kirim Map
    frame_kirimap = customtkinter.CTkFrame(master=frame_right, corner_radius=0, fg_color='transparent')
    frame_kirimap.grid(row=2, column=2, rowspan=1, pady=0, padx=0, sticky="nsew")
    
    label_lat = customtkinter.CTkLabel(frame_kirimap, text="Latitude:", anchor="w")
    label_lat.grid(row=2, column=0, padx=(12, 0), pady=0, sticky='wn')
    
    entry2 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="Latitude")
    entry2.grid(row=3, column=0, sticky="wn", padx=(12, 0), pady=0)
    
    label_long = customtkinter.CTkLabel(frame_kirimap, text="Longitude:", anchor="w")
    label_long.grid(row=4, column=0, padx=(12, 0), pady=0, sticky='wn')

    entry3 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="Longitude")
    entry3.grid(row=5, column=0, sticky="wn", padx=(12, 0), pady=0)

    entry2.configure(state='disabled') 
    entry3.configure(state='disabled') 

    label_timezone = customtkinter.CTkLabel(frame_kirimap, text="Time Zone:", anchor="w")
    label_timezone.grid(row=6, column=0, padx=(12, 0), pady=0, sticky='wn')

    entry4 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="Time Zone")
    entry4.grid(row=7, column=0, sticky="wn", padx=(12, 0), pady=0)

    label_elevation = customtkinter.CTkLabel(frame_kirimap, text="Elevation (m):", anchor="w")
    label_elevation.grid(row=8, column=0, padx=(12, 0), pady=0, sticky='wn')

    entry5 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="Elevation")
    entry5.grid(row=9, column=0, sticky="wn", padx=(12, 0), pady=0)

    #Tombol "Clear Markers"
    button_2 = customtkinter.CTkButton(master=frame_kirimap, text="Clear Markers", command=clear_marker_event)
    button_2.grid(pady=(3, 0), padx=(12, 12), row=10, column=0)
     
    #Entri Tahun
    frame_label = customtkinter.CTkFrame(master=frame_kirimap, corner_radius=0, fg_color='transparent')
    frame_label.grid(row=11, column=0, pady=0, padx=0, sticky="nsew")   
    #Label Date
    label_Tanggal = customtkinter.CTkLabel(frame_label, text="Date :", anchor="w")
    label_Tanggal.grid(row=1, column=0, padx=(12, 0), pady=0, sticky='wn')
    
    #Checkbox untuk tanggal sekarang
    def cek():
        if cek_var.get():
            tanggal_sekarang = datetime.datetime.now().date()
            hari = tanggal_sekarang.day
            bulan = tanggal_sekarang.month
            tahun = tanggal_sekarang.year
            if cek_var1.get():
                h_hijri, b_hijri, Tt_hijri, JulianDay, JulianDayGMT, jam_hijri, menit_hijri = gregorian_to_hijri(int(tahun), bulan, hari, 0, 0, 0)
                entry6.delete(0, 'end')
                entry6.insert(0, Tt_hijri)

                selected_month = conv_angka_to_bulan_hijri(b_hijri)
                bulan_menu.set(selected_month)
                tanggal_menu.set(h_hijri)

                entry6.configure(state='disabled')
                bulan_menu.configure(state='disabled')
                tanggal_menu.configure(state='disabled')

                menu_bulan(selected_month)
            
            else:
                entry6.delete(0, 'end')
                entry6.insert(0, tahun)

                selected_month = conv_angka_to_bulan_grego(bulan)
                bulan_menu.set(selected_month)
                tanggal_menu.set(hari)

                entry6.configure(state='disabled')
                bulan_menu.configure(state='disabled')
                tanggal_menu.configure(state='disabled')

                menu_bulan(selected_month)
        
        else:
            entry6.configure(state='normal')
            bulan_menu.configure(state='normal')
            tanggal_menu.configure(state='normal')

    cek_var = tk.BooleanVar(value=True)
    checkbox1 = tk.Checkbutton(master=frame_label, text='Now', variable=cek_var, command=cek)
    checkbox1.grid(row=1, column=1, padx=(5, 12), pady=(5,0), sticky='wn')

    def cek_bulan():
        if cek_var1.get():
            cetak_bulan = ["Muharram", "Shafar", "Rabiul Awal", "Rabiul Akhir", "Jumadil Awal", 
                            "Jumadil Akhir", "Rajab", "Sya'ban", "Ramadhan", "Syawal", "Dzulkaidah",
                            "Dzulhijjah"]
            bulan_menu.configure(values = cetak_bulan)
        else:
            cetak_bulan = ["January", "February", "March", "April", "May", "June", "July", "August",
                            "September", "October", "November", "December"]
            bulan_menu.configure(values = cetak_bulan)

    cek_var1 = tk.BooleanVar()
    checkbox2 = tk.Checkbutton(master=frame_label, text='Hijri', variable=cek_var1, command=cek_bulan)
    checkbox2.grid(row=1, column=1, padx=(65, 12), pady=(5,0), sticky='wn')

    #Data Tahun
    entry6 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="YYYY")
    entry6.grid(row=12, column=0, sticky="wn", padx=(10, 10), pady=0)

    def menu_bulan(x):
        selected_year = int(entry6.get())
        if cek_var1.get():
            selected_month = conv_bulan_hijri_to_angka(x)
            date_values = hitung_jumlah_hari_bulan_hijri((selected_year), (selected_month))
            # Update nilai (values) pada tanggal_menu
            tanggal_menu.configure(values=(date_values))
        else:
            selected_month = conv_bulan_grego_to_angka(x)
            date_values = hitung_jumlah_hari_bulan_grego(selected_year, selected_month)
            # Update nilai (values) pada tanggal_menu
            tanggal_menu.configure(values=(date_values))

    def menu_tanggal(x):
        None

    bulan_menu = customtkinter.CTkOptionMenu(frame_kirimap, values=["January", "February",
                                             "March", "April", "May", "June", "July", "August",
                                              "September", "October", "November", "December"],
                                               command=menu_bulan)
    bulan_menu.grid(row=13, column=0, sticky="we", padx=(12, 12), pady=(3, 0))   

    tanggal_menu = customtkinter.CTkOptionMenu(frame_kirimap, values=[""],
                                               command=menu_tanggal(0))
    tanggal_menu.grid(row=14, column=0, sticky="we", padx=(12, 12), pady=(3, 0))

    #Isian tanggal awal
    tanggal_sekarang = datetime.datetime.now().date()
    hari = tanggal_sekarang.day
    bulan = tanggal_sekarang.month
    tahun = tanggal_sekarang.year
    entry6.delete(0, 'end')
    entry6.insert(0, tahun)

    selected_month = conv_angka_to_bulan_grego(bulan)
    bulan_menu.set(selected_month)
    tanggal_menu.set(hari)
    entry6.configure(state='disabled')
    bulan_menu.configure(state='disabled')
    tanggal_menu.configure(state='disabled')
    menu_bulan(selected_month)

    #Default
    subuhdegree1 = []
    isyadegree1 = []
    asharshadow1 = []
    correction1 = []
    imsaktime1 = []
    duhatime1 = []
    subuhdegree1.append(-20)
    isyadegree1.append(-18)
    asharshadow1.append(1)
    correction1.append(2)
    imsaktime1.append(-10)
    duhatime1.append(20)

    #Ketika Tombol Set Data diklik
    def set_data():
        tahun = int(entry6.get())
        hari = int(tanggal_menu.get())
        lintang = float(entry2.get())
        bujur = float(entry3.get())
        zona = float(entry4.get())
        ketinggian = float(entry5.get())

        subuhdegree = subuhdegree1[-1]
        isyadegree = isyadegree1[-1]
        asharshadow = asharshadow1[-1]
        correction = correction1[-1]
        imsaktime = imsaktime1[-1]
        duhatime = duhatime1[-1]

        if cek_var1.get():
            bulan = int(conv_bulan_hijri_to_angka(bulan_menu.get()))
            h_grego, b_grego, Tt_grego, Julian_Day, JulianDayGMT, jam_grego, menit_grego = hijri_to_grego(tahun, bulan, hari, zona, 0, 0)
            bulan_grego = conv_angka_to_bulan_grego(b_grego)
            pos = tkintermapview.convert_coordinates_to_address(lintang, bujur)

            #Hitung hari tersebut
            hari_ini = apakah_hari_ini(Julian_Day, zona)

            #Hitung hari jawa
            hari_inijawa = weton_hari_ini(Julian_Day, zona) 

            text1 = f"Prayer Time in : {pos.city}, {pos.state}, {pos.country}, Postal Code {pos.postal}\nat : {hari_ini}, {hari_inijawa}, {hari} {bulan_menu.get()} {tahun} H / {h_grego} {bulan_grego} {Tt_grego} M"
            label_keterangan.configure(text= text1, justify='left')
        #Convert Grego Hijri dan Nilai JD
        else:
            bulan = int(conv_bulan_grego_to_angka(bulan_menu.get()))
            hari_hijri, bulan_hijri, tahun_hijri, Julian_Day, JulianDayGMT, jam_hijri, menit_hijri = gregorian_to_hijri(tahun, bulan, hari, zona, 0, 0)
        
            bulan_hijriyah = conv_angka_to_bulan_hijri(bulan_hijri)
            pos = tkintermapview.convert_coordinates_to_address(lintang, bujur)
        
            #Hitung hari tersebut
            hari_ini = apakah_hari_ini(Julian_Day, zona)

            #Hitung hari jawa
            hari_inijawa = weton_hari_ini(Julian_Day, zona) 

            text1 = f"Prayer Times in : {pos.city}, {pos.state}, {pos.country}, Postal Code {pos.postal}\nat : {hari_ini}, {hari_inijawa}, {hari} {bulan_menu.get()} {tahun} M / {hari_hijri} {bulan_hijriyah} {tahun_hijri} H"
            label_keterangan.configure(text= text1, justify='left')
                   #Hitung Waktu Sholat
        
        #Hitung Waktu Sholat
        JamDzuhur, MenitDzuhur, JamAshar, MenitAshar, JamMaghrib, MenitMaghrib, JamIsya, MenitIsya, JamSubuh, MenitSubuh, JamTerbit, MenitTerbit, JamImsak, MenitImsak, JamDuha, MenitDuha = hitung_waktu_sholat(Julian_Day, bujur, lintang, ketinggian, zona, subuhdegree, isyadegree, asharshadow, correction, imsaktime, duhatime)
        
        label_subuh.configure(state='normal')
        label_subuh.delete(0, 'end')
        label_subuh.insert(0, f"Subuh   : [{JamSubuh}:{MenitSubuh}]")
        label_subuh.configure(state='disabled')   

        label_terbit.configure(state='normal')
        label_terbit.delete(0, 'end')
        label_terbit.insert(0, f"Rise       : [{JamTerbit}:{MenitTerbit}]")
        label_terbit.configure(state='disabled')  

        label_duha.configure(state='normal')
        label_duha.delete(0, 'end')
        label_duha.insert(0, f"Duha    : [{JamDuha}:{MenitDuha}]")
        label_duha.configure(state='disabled')   

        label_imsak.configure(state='normal')
        label_imsak.delete(0, 'end')
        label_imsak.insert(0, f"Imsak   : [{JamImsak}:{MenitImsak}]")
        label_imsak.configure(state='disabled')  

        label_dzuhur.configure(state='normal')
        label_dzuhur.delete(0, 'end')
        label_dzuhur.insert(0, f"Dzuhur : [{JamDzuhur}:{MenitDzuhur}]")
        label_dzuhur.configure(state='disabled')   

        label_ashar.configure(state='normal')
        label_ashar.delete(0, 'end')
        label_ashar.insert(0, f"Ashar    : [{JamAshar}:{MenitAshar}]")
        label_ashar.configure(state='disabled')  

        label_maghrib.configure(state='normal')
        label_maghrib.delete(0, 'end')
        label_maghrib.insert(0, f"Maghrib : [{JamMaghrib}:{MenitMaghrib}]")
        label_maghrib.configure(state='disabled')   

        label_isya.configure(state='normal')
        label_isya.delete(0, 'end')
        label_isya.insert(0, f"Isya      : [{JamIsya}:{MenitIsya}]")
        label_isya.configure(state='disabled')  
        
    #Tombol "Set Data"
    button_3 = customtkinter.CTkButton(master=frame_kirimap, text="Set Data", command=set_data)
    button_3.grid(pady=(3, 0), padx=(12, 12), row=15, column=0)
    
    #Frame Bawah Map
    frame_bawahmap = customtkinter.CTkFrame(master=frame_right, corner_radius=0, fg_color='transparent')
    frame_bawahmap.grid(row=3, column=0, columnspan=3, pady=0, padx=0, sticky="nsew")
    #Label Keterangan
    label_keterangan = customtkinter.CTkLabel(frame_bawahmap, text="Prayer Times in : None\nat : None", font=('',14), anchor="w", justify='left')
    label_keterangan.grid(row=0, column=0, columnspan=3, padx=(12, 12), pady=(10,5), sticky='wn')

    #Keterangan Algoritma
    def algoritma():
        root1 = customtkinter.CTk()
        root1.title("Algoritm")
        root1.geometry(f"{200}x{500}")
        root1.minsize(200, 500)
        root1.geometry(f"+{50}+{50}")
        
        def setting():
            subuhdegree1.append(entry_subuhdegree.get())
            isyadegree1.append(entry_isyadegree.get())
            asharshadow1.append(entry_asharshadow.get())
            correction1.append(entry_correction.get())
            imsaktime1.append(entry_imsaktime.get())
            duhatime1.append(entry_duhatime.get())
            set_data()
            root1.withdraw()

        frame_algoritma = customtkinter.CTkFrame(master=root1, corner_radius=0, fg_color='transparent')
        frame_algoritma.grid(row=0, column=0, pady=0, padx=0, sticky="nsew")
        
        label_subuhdegree = customtkinter.CTkLabel(frame_algoritma, text="Subuh Degree:", anchor="w")
        label_subuhdegree.grid(row=0, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_subuhdegree = customtkinter.CTkOptionMenu(frame_algoritma, values=['-6', '-7', '-8', '-9', '-10', '-11','-12', '-13', '-14', '-15', '-16', '-17', '-18', '-19', '-20'],
                                                           )
        entry_subuhdegree.grid(row=1, column=0, padx=(12, 20), pady=(0),sticky='wn')
        entry_subuhdegree.set(subuhdegree1[-1])

        label_isyadegree = customtkinter.CTkLabel(frame_algoritma, text="Isya Degree:", anchor="w")
        label_isyadegree.grid(row=2, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_isyadegree = customtkinter.CTkOptionMenu(frame_algoritma, values=['-6', '-7', '-8', '-9', '-10', '-11','-12', '-13', '-14', '-15', '-16', '-17', '-18', '-19', '-20'],
                                                           )
        entry_isyadegree.grid(row=3, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_isyadegree.set(isyadegree1[-1])

        label_asharshadow = customtkinter.CTkLabel(frame_algoritma, text="Ashar Shadow:", anchor="w")
        label_asharshadow.grid(row=4, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_asharshadow = customtkinter.CTkOptionMenu(frame_algoritma, values=['1', '2'],
                                                           )
        entry_asharshadow.grid(row=5, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_asharshadow.set(asharshadow1[-1])

        label_correction = customtkinter.CTkLabel(frame_algoritma, text="Correction: ", anchor="w")
        label_correction.grid(row=6, column=0, padx=(12, 0), pady=0, sticky='wn')
        label_correction1 = customtkinter.CTkLabel(frame_algoritma, text="(+ minutes from Prayer Times)", font=('', 11), anchor="w")
        label_correction1.grid(row=7, column=0, padx=(12, 0), pady=0, sticky='wn') 

        entry_correction = customtkinter.CTkOptionMenu(frame_algoritma, values=['0', '1', '2', '3', '4', '5', '6'],
                                                           )
        entry_correction.grid(row=8, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_correction.set(correction1[-1])

        label_imsaktime = customtkinter.CTkLabel(frame_algoritma, text="Imsak Time: ", anchor="w")
        label_imsaktime.grid(row=9, column=0, padx=(12, 0), pady=0, sticky='wn')
        label_imsaktime1 = customtkinter.CTkLabel(frame_algoritma, text="(+ minutes from Subuh Time)", font=('', 11), anchor="w")
        label_imsaktime1.grid(row=10, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_imsaktime = customtkinter.CTkOptionMenu(frame_algoritma, values=['-6', '-7', '-8', '-9', '-10', '-11','-12'],
                                                           )
        entry_imsaktime.grid(row=11, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_imsaktime.set(imsaktime1[-1])

        label_duhatime = customtkinter.CTkLabel(frame_algoritma, text="Duha Time: ", anchor="w")
        label_duhatime.grid(row=12, column=0, padx=(12, 0), pady=0, sticky='wn')
        label_duhatime = customtkinter.CTkLabel(frame_algoritma, text="(+ minutes from Rise Time)", font=('', 11), anchor="w")
        label_duhatime.grid(row=13, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_duhatime = customtkinter.CTkOptionMenu(frame_algoritma, values=['16', '17', '18', '19', '20', '21', '22', '23', '24'],
                                                           )
        entry_duhatime.grid(row=14, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_duhatime.set(duhatime1[-1])

        set_algo = customtkinter.CTkButton(frame_algoritma, text="Set Algoritm", command=setting)
        set_algo.grid(row=15, column=0, padx=(12, 20), pady=(10,0), sticky='wn')
        
        def default():
            entry_subuhdegree.set(-20)
            entry_isyadegree.set(-18)
            entry_asharshadow.set(1)
            entry_correction.set(2)
            entry_imsaktime.set(-10)
            entry_duhatime.set(20)

        set_default = customtkinter.CTkButton(frame_algoritma, text="Default", command=default)
        set_default.grid(row=16, column=0, padx=(12, 20), pady=(5,0), sticky='wn')

        subuhdegree = entry_subuhdegree.get()
        isyadegree = entry_isyadegree.get()
        asharshadow = entry_asharshadow.get()
        correction = entry_correction.get()
        imsaktime = entry_imsaktime.get()
        duhatime = entry_duhatime.get()
        
        def on_focus_out(event):
            root1.withdraw()

        # Menambahkan event handler untuk event FocusOut
        root1.bind('<FocusOut>', on_focus_out)
        
        root1.mainloop()

    algoritma1 = customtkinter.CTkButton(frame_bawahmap, text="Algoritm", command=algoritma, width=10, height=2)
    algoritma1.grid(row=0, column=3, padx=(12, 20), pady=(2,8))


    #Label Keterangan
    label_imsak = customtkinter.CTkEntry(frame_bawahmap, placeholder_text="Imsak",font=('Arial Bold',14), justify='left')
    label_imsak.grid(row=1, column=0, padx=(12, 20), pady=0, sticky='wn')   
    label_subuh = customtkinter.CTkEntry(frame_bawahmap, placeholder_text="Subuh",font=('Arial Bold',14), justify='left')
    label_subuh.grid(row=1, column=1, padx=(12, 20), pady=(1,0), sticky='wn')
    label_terbit = customtkinter.CTkEntry(frame_bawahmap, placeholder_text="Rise",font=('Arial Bold',14), justify='left')
    label_terbit.grid(row=1, column=2, padx=(12, 20), pady=0, sticky='wn')
    label_duha = customtkinter.CTkEntry(frame_bawahmap, placeholder_text="Duha",font=('Arial Bold',14), justify='left')
    label_duha.grid(row=1, column=3, padx=(12, 20), pady=0, sticky='wn')
    label_dzuhur = customtkinter.CTkEntry(frame_bawahmap, placeholder_text="Dzuhur",font=('Arial Bold',14), justify='left')
    label_dzuhur.grid(row=2, column=0, padx=(12, 20), pady=0, sticky='wn')
    label_ashar = customtkinter.CTkEntry(frame_bawahmap, placeholder_text="Ashar",font=('Arial Bold',14), justify='left')
    label_ashar.grid(row=2, column=1, padx=(12, 20), pady=0, sticky='wn')
    label_maghrib = customtkinter.CTkEntry(frame_bawahmap, placeholder_text="Maghrib",font=('Arial Bold',14), justify='left')
    label_maghrib.grid(row=2, column=2, padx=(12, 20), pady=0, sticky='wn')
    label_isya = customtkinter.CTkEntry(frame_bawahmap, placeholder_text="Isya",font=('Arial Bold',14), justify='left')
    label_isya.grid(row=2, column=3, padx=(12, 20), pady=0, sticky='wn')

    label_subuh.configure(state='disabled') 
    label_terbit.configure(state='disabled') 
    label_duha.configure(state='disabled') 
    label_imsak.configure(state='disabled') 
    label_dzuhur.configure(state='disabled') 
    label_ashar.configure(state='disabled') 
    label_maghrib.configure(state='disabled') 
    label_isya.configure(state='disabled') 

    #Set nilai default
    map_widget.set_position(-7.9526251, 112.6145089) #Posisi Universitas Brawijaya
    map_widget.set_zoom(10)
    map_option_menu.set("OpenStreetMap")

    # Klik kanan untuk menambah lokasi
    map_widget.add_right_click_menu_command(label="Add Location",
                                        command=set_marker_event,
                                        pass_coords=True)

def tombol_monthlyprayer():
    for widget in frame_right.winfo_children():
        widget.destroy()
    set_button_highlight(button_waktusholat2)
    # List untuk menyimpan marker
    marker_list = []
    
    def set_marker_event(coords):
        for marker in marker_list:
            marker.delete()
        marker_list.append(map_widget.set_marker(coords[0], coords[1])) 

        #Input Entry Lat dan Lng
        entry2.configure(state='normal')
        entry2.delete(0, 'end')
        entry2.insert(0, str(coords[0]))  # Latitude
        entry2.configure(state='disabled')
        entry3.configure(state='normal')
        entry3.delete(0, 'end')
        entry3.insert(0, str(coords[1]))  # Longitude  
        entry3.configure(state='disabled') 

        #Mencari Nilai Time Zone
        tf = timezonefinder.TimezoneFinder()
        #Mendapatkan nama zona waktu sesuai database pada pytz
        timezone_str = tf.certain_timezone_at(lat=coords[0], lng=coords[1])
        if timezone_str is None:
            entry4.delete(0, 'end')
            entry4.insert(0, '0')
        else:
            timezone = pytz.timezone(timezone_str)
            utc_offset_hours = timezone.utcoffset(datetime.datetime.utcnow()).total_seconds()/3600
            entry4.delete(0, 'end')
            entry4.insert(0, (utc_offset_hours))            
        
        #Melakukan penentuan ketinggian
        heigh = ketinggian(coords[0], coords[1])
        if heigh is not None:
            entry5.delete(0, 'end')
            entry5.insert(0, heigh)
        else:
            entry4.delete(0, 'end')
            entry4.insert(0, '0')         

    def clear_marker_event():
        for marker in marker_list:
            marker.delete()
        entry.configure(state='normal')
        entry.delete(0, 'end')      
        entry.configure(placeholder_text="type address")
        entry2.configure(state='normal')
        entry2.delete(0, 'end')    
        entry2.configure(placeholder_text="Latitude")
        entry2.configure(state='disabled')
        entry3.configure(state='normal')
        entry3.delete(0, 'end')      
        entry3.configure(placeholder_text="Longitude")
        entry3.configure(state='disabled')
        entry4.configure(state='normal')
        entry4.delete(0, 'end')      
        entry4.configure(placeholder_text="Time Zone")
        entry5.configure(state='normal')
        entry5.delete(0, 'end')      
        entry5.configure(placeholder_text="Elevation")
        cek_varloc.set(False)

    def search_event(event=None):
        map_widget.set_address(entry.get())
        for marker in marker_list:
            marker.delete()
        x, y = tkintermapview.convert_address_to_coordinates(entry.get())
        marker_list.append(map_widget.set_marker(x, y))
        
        #Input Entry Lat dan Lng
        entry2.configure(state='normal')
        entry2.delete(0, 'end')
        entry2.insert(0, str(x))  # Latitude
        entry2.configure(state='disabled')
        entry3.configure(state='normal')
        entry3.delete(0, 'end')
        entry3.insert(0, str(y))  # Longitude  
        entry3.configure(state='disabled') 

        #Mencari Nilai Time Zone
        tf = timezonefinder.TimezoneFinder()
        #Mendapatkan nama zona waktu sesuai database pada pytz
        timezone_str = tf.certain_timezone_at(lat=x, lng=y)
        if timezone_str is None:
            entry4.delete(0, 'end')
            entry4.insert(0, '0')
        else:
            timezone = pytz.timezone(timezone_str)
            utc_offset_hours = timezone.utcoffset(datetime.datetime.utcnow()).total_seconds()/3600
            entry4.delete(0, 'end')
            entry4.insert(0, (utc_offset_hours))            
        
        #Melakukan penentuan ketinggian
        heigh = ketinggian(x, y)
        if heigh is not None:
            entry5.delete(0, 'end')
            entry5.insert(0, heigh)
        else:
            entry4.delete(0, 'end')
            entry4.insert(0, '0')  

    def change_map(new_map: str):
        if new_map == "OpenStreetMap":
            map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "GoogleMap":
            map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "GoogleSatellite":
            map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    #Label add location
    label_location = customtkinter.CTkLabel(frame_right, text="Add Location:    (Right Click to edit and add Marker)", anchor="w")
    label_location.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky='wn')

    # Kotak teks untuk pencarian alamat
    entry = customtkinter.CTkEntry(master=frame_right, placeholder_text="type address")
    entry.grid(row=1, column=0, sticky="we", padx=(12, 0), pady=0)
    entry.bind("<Return>", search_event)

    def cek_location():
        if cek_varloc.get():
            g = geocoder.ip('me')
            x, y = g.latlng
            currentlocation = tkintermapview.convert_coordinates_to_address(x, y)
            entry.configure(state='normal')
            entry.delete(0, 'end')
            entry.insert(0, (f"{currentlocation.city}, {currentlocation.state}, {currentlocation.country}"))
            map_widget.set_position(x, y)
            entry.configure(state='disabled')
            for marker in marker_list:
                marker.delete()
            marker_list.append(map_widget.set_marker(x, y))

            #Input Entry Lat dan Lng
            entry2.configure(state='normal')
            entry2.delete(0, 'end')
            entry2.insert(0, str(x))  # Latitude
            entry2.configure(state='disabled')
            entry3.configure(state='normal')
            entry3.delete(0, 'end')
            entry3.insert(0, str(y))  # Longitude  
            entry3.configure(state='disabled') 

            #Mencari Nilai Time Zone
            tf = timezonefinder.TimezoneFinder()
            #Mendapatkan nama zona waktu sesuai database pada pytz
            timezone_str = tf.certain_timezone_at(lat=x, lng=y)
            if timezone_str is None:
                entry4.delete(0, 'end')
                entry4.insert(0, '0')
            else:
                timezone = pytz.timezone(timezone_str)
                utc_offset_hours = timezone.utcoffset(datetime.datetime.utcnow()).total_seconds()/3600
                entry4.delete(0, 'end')
                entry4.insert(0, (utc_offset_hours))            
        
            #Melakukan penentuan ketinggian
            heigh = ketinggian(x, y)
            if heigh is not None:
                entry5.delete(0, 'end')
                entry5.insert(0, heigh)
            else:
                entry4.delete(0, 'end')
                entry4.insert(0, '0')  

        else:
            entry.configure(state='normal')
            entry.delete(0, 'end')      
            entry.configure(placeholder_text="type address")
            entry2.configure(state='normal')
            entry2.delete(0, 'end')    
            entry2.configure(placeholder_text="Latitude")
            entry2.configure(state='disabled')
            entry3.configure(state='normal')
            entry3.delete(0, 'end')      
            entry3.configure(placeholder_text="Longitude")
            entry3.configure(state='disabled')
            entry4.configure(state='normal')
            entry4.delete(0, 'end')      
            entry4.configure(placeholder_text="Time Zone")
            entry5.configure(state='normal')
            entry5.delete(0, 'end')      
            entry5.configure(placeholder_text="Elevation")
            for marker in marker_list:
                marker.delete()    

    cek_varloc = tk.BooleanVar()
    checkboxloc = tk.Checkbutton(master=frame_right, text='Current Location with IP', variable=cek_varloc, command=cek_location)
    checkboxloc.grid(row=0, column=1, padx=(0, 0), pady=(12,12), sticky='wn')

    #Tombol "Search"
    button_5 = customtkinter.CTkButton(master=frame_right, text="Search", width=90, command=search_event)
    button_5.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=0)

    # Widget peta
    map_widget = TkinterMapView(frame_right, corner_radius=0)
    map_widget.grid(row=2, column=0, columnspan=2, sticky="nswe", padx=(10, 10), pady=(10, 10))

    # Pilihan Model Map
    map_label = customtkinter.CTkLabel(frame_right, text="Maps Mode:", anchor="w")
    map_label.grid(row=0, column=2, padx=(12, 0), pady=(10, 0), sticky='wn')
    map_option_menu = customtkinter.CTkOptionMenu(frame_right, values=["OpenStreetMap", "GoogleMap", "GoogleSatellite"],
                                               command=change_map)
    map_option_menu.grid(row=1, column=2, sticky="we", padx=(12, 12), pady=0)
    
    #Frame Kirim Map
    frame_kirimap = customtkinter.CTkFrame(master=frame_right, corner_radius=0, fg_color='transparent')
    frame_kirimap.grid(row=2, column=2, rowspan=1, pady=0, padx=0, sticky="nsew")
    
    label_lat = customtkinter.CTkLabel(frame_kirimap, text="Latitude:", anchor="w")
    label_lat.grid(row=2, column=0, padx=(12, 0), pady=0, sticky='wn')
    
    entry2 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="Latitude")
    entry2.grid(row=3, column=0, sticky="wn", padx=(12, 0), pady=0)
    
    label_long = customtkinter.CTkLabel(frame_kirimap, text="Longitude:", anchor="w")
    label_long.grid(row=4, column=0, padx=(12, 0), pady=0, sticky='wn')

    entry3 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="Longitude")
    entry3.grid(row=5, column=0, sticky="wn", padx=(12, 0), pady=0)

    entry2.configure(state='disabled') 
    entry3.configure(state='disabled') 

    label_timezone = customtkinter.CTkLabel(frame_kirimap, text="Time Zone:", anchor="w")
    label_timezone.grid(row=6, column=0, padx=(12, 0), pady=0, sticky='wn')

    entry4 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="Time Zone")
    entry4.grid(row=7, column=0, sticky="wn", padx=(12, 0), pady=0)

    label_elevation = customtkinter.CTkLabel(frame_kirimap, text="Elevation (m):", anchor="w")
    label_elevation.grid(row=8, column=0, padx=(12, 0), pady=0, sticky='wn')

    entry5 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="Elevation")
    entry5.grid(row=9, column=0, sticky="wn", padx=(12, 0), pady=0)

    #Tombol "Clear Markers"
    button_2 = customtkinter.CTkButton(master=frame_kirimap, text="Clear Markers", command=clear_marker_event)
    button_2.grid(pady=(10, 0), padx=(12, 12), row=10, column=0)
     
    #Entri Tahun
    frame_label = customtkinter.CTkFrame(master=frame_kirimap, corner_radius=0, fg_color='transparent')
    frame_label.grid(row=11, column=0, pady=0, padx=0, sticky="nsew")   
    #Label Date
    label_Tanggal = customtkinter.CTkLabel(frame_label, text="Date :", anchor="w")
    label_Tanggal.grid(row=1, column=0, padx=(12, 0), pady=0, sticky='wn')
    
    #Checkbox untuk tanggal sekarang
    def cek():
        if cek_var.get():
            tanggal_sekarang = datetime.datetime.now().date()
            hari = tanggal_sekarang.day
            bulan = tanggal_sekarang.month
            tahun = tanggal_sekarang.year
            if cek_var1.get():
                h_hijri, b_hijri, Tt_hijri, JulianDay, JulianDayGMT, jam_hijri, menit_hijri = gregorian_to_hijri(int(tahun), bulan, hari, 0, 0, 0)
                entry6.delete(0, 'end')
                entry6.insert(0, Tt_hijri)

                selected_month = conv_angka_to_bulan_hijri(b_hijri)
                bulan_menu.set(selected_month)
                #tanggal_menu.set(h_hijri)

                entry6.configure(state='disabled')
                bulan_menu.configure(state='disabled')
                #tanggal_menu.configure(state='disabled')

                menu_bulan(selected_month)
            
            else:
                entry6.delete(0, 'end')
                entry6.insert(0, tahun)

                selected_month = conv_angka_to_bulan_grego(bulan)
                bulan_menu.set(selected_month)
                #tanggal_menu.set(hari)

                entry6.configure(state='disabled')
                bulan_menu.configure(state='disabled')
                #tanggal_menu.configure(state='disabled')

                menu_bulan(selected_month)
        
        else:
            entry6.configure(state='normal')
            bulan_menu.configure(state='normal')
            #tanggal_menu.configure(state='normal')

    cek_var = tk.BooleanVar(value=True)
    checkbox1 = tk.Checkbutton(master=frame_label, text='Now', variable=cek_var, command=cek)
    checkbox1.grid(row=1, column=1, padx=(5, 12), pady=(5,0), sticky='wn')

    def cek_bulan():
        if cek_var1.get():
            cetak_bulan = ["Muharram", "Shafar", "Rabiul Awal", "Rabiul Akhir", "Jumadil Awal", 
                            "Jumadil Akhir", "Rajab", "Sya'ban", "Ramadhan", "Syawal", "Dzulkaidah",
                            "Dzulhijjah"]
            bulan_menu.configure(values = cetak_bulan)
        else:
            cetak_bulan = ["January", "February", "March", "April", "May", "June", "July", "August",
                            "September", "October", "November", "December"]
            bulan_menu.configure(values = cetak_bulan)

    cek_var1 = tk.BooleanVar()
    checkbox2 = tk.Checkbutton(master=frame_label, text='Hijri', variable=cek_var1, command=cek_bulan)
    checkbox2.grid(row=1, column=1, padx=(65, 12), pady=(5,0), sticky='wn')

    #Data Tahun
    entry6 = customtkinter.CTkEntry(master=frame_kirimap, placeholder_text="YYYY")
    entry6.grid(row=12, column=0, sticky="wn", padx=(10, 10), pady=0)

    def menu_bulan(x):
        selected_year = int(entry6.get())
        if cek_var1.get():
            selected_month = conv_bulan_hijri_to_angka(x)
            date_values = hitung_jumlah_hari_bulan_hijri((selected_year), (selected_month))
            # Update nilai (values) pada tanggal_menu
            #tanggal_menu.configure(values=(date_values))
        else:
            selected_month = conv_bulan_grego_to_angka(x)
            date_values = hitung_jumlah_hari_bulan_grego(selected_year, selected_month)
            # Update nilai (values) pada tanggal_menu
            #tanggal_menu.configure(values=(date_values))
        return date_values

    bulan_menu = customtkinter.CTkOptionMenu(frame_kirimap, values=["January", "February",
                                             "March", "April", "May", "June", "July", "August",
                                              "September", "October", "November", "December"],
                                               command=menu_bulan)
    bulan_menu.grid(row=13, column=0, sticky="we", padx=(12, 12), pady=(5,0))   


    #Isian tanggal awal
    tanggal_sekarang = datetime.datetime.now().date()
    tahun = tanggal_sekarang.year
    bulan = tanggal_sekarang.month

    entry6.delete(0, 'end')
    entry6.insert(0, tahun)

    selected_month = conv_angka_to_bulan_grego(bulan)
    bulan_menu.set(selected_month)

    entry6.configure(state='disabled')
    bulan_menu.configure(state='disabled')

    menu_bulan(selected_month)

    subuhdegree1 = []
    isyadegree1 = []
    asharshadow1 = []
    correction1 = []
    imsaktime1 = []
    duhatime1 = []
    subuhdegree1.append(-20)
    isyadegree1.append(-18)
    asharshadow1.append(1)
    correction1.append(2)
    imsaktime1.append(-10)
    duhatime1.append(20)

    #Ketika Tombol Set Data diklik
    def set_data():
        tahun = int(entry6.get())
        hari = menu_bulan(bulan_menu.get())
        lintang = float(entry2.get())
        bujur = float(entry3.get())
        zona = float(entry4.get())
        ketinggian = float(entry5.get())
        pos = tkintermapview.convert_coordinates_to_address(lintang, bujur)
        text1 = f"Prayer Times in : {pos.city}, {pos.state}, {pos.country}, Postal Code {pos.postal}, at : {bulan_menu.get()} {tahun}"
        label_keterangan.configure(text= text1, justify='left')

        subuhdegree = subuhdegree1[-1]
        isyadegree = isyadegree1[-1]
        asharshadow = asharshadow1[-1]
        correction = correction1[-1]
        imsaktime = imsaktime1[-1]
        duhatime = duhatime1[-1]
        
        def perhari(hari):
            if cek_var1.get():
                bulan = int(conv_bulan_hijri_to_angka(bulan_menu.get()))
                h_grego, b_grego, Tt_grego, Julian_Day, JulianDayGMT, jam_grego, menit_grego = hijri_to_grego(tahun, bulan, hari, zona, 0, 0)
                bulan_grego = conv_angka_to_bulan_grego(b_grego)

                #Hitung hari tersebut
                hari_ini = apakah_hari_ini(Julian_Day, zona)

                #Hitung hari jawa
                hari_inijawa = weton_hari_ini(Julian_Day, zona) 

                textTanggal = f"{hari_ini}, {hari_inijawa}, {hari} / {h_grego} {bulan_grego} {Tt_grego} M"
            #Convert Grego Hijri dan Nilai JD
            else:
                bulan = int(conv_bulan_grego_to_angka(bulan_menu.get()))
                hari_hijri, bulan_hijri, tahun_hijri, Julian_Day, JulianDayGMT, jam_hijri, menit_hijri = gregorian_to_hijri(tahun, bulan, hari, zona, 0, 0)
        
                bulan_hijriyah = conv_angka_to_bulan_hijri(bulan_hijri)
                
                #Hitung hari tersebut
                hari_ini = apakah_hari_ini(Julian_Day, zona)

                #Hitung hari jawa
                hari_inijawa = weton_hari_ini(Julian_Day, zona) 

                textTanggal = f"{hari_ini}, {hari_inijawa}, {hari} / {hari_hijri} {bulan_hijriyah} {tahun_hijri} H"

            #Hitung Waktu Sholat
            JamDzuhur, MenitDzuhur, JamAshar, MenitAshar, JamMaghrib, MenitMaghrib, JamIsya, MenitIsya, JamSubuh, MenitSubuh, JamTerbit, MenitTerbit, JamImsak, MenitImsak, JamDuha, MenitDuha = hitung_waktu_sholat(Julian_Day, bujur, lintang, ketinggian, zona, subuhdegree, isyadegree, asharshadow, correction, imsaktime, duhatime)
            textsubuh = f"{JamSubuh}:{MenitSubuh}"
            textterbit = f"{JamTerbit}:{MenitTerbit}"
            textduha = f"{JamDuha}:{MenitDuha}"
            textimsak = f"{JamImsak}:{MenitImsak}"
            textdzuhur = f"{JamDzuhur}:{MenitDzuhur}"
            textashar = f"{JamAshar}:{MenitAshar}"
            textmaghrib = f"{JamMaghrib}:{MenitMaghrib}"
            textisya= f"{JamIsya}:{MenitIsya}"

            return textTanggal, textimsak, textsubuh, textterbit, textduha, textdzuhur, textashar, textmaghrib, textisya

        i = 0
        Date = []
        Imsak = []
        Subuh = []
        Terbit = []
        Duha = []
        Dzuhur = []
        Ashar = []
        Maghrib = []
        Isya = []
        for i in range(len(hari)):
            textTanggal, textimsak, textsubuh, textterbit, textduha, textdzuhur, textashar, textmaghrib, textisya = perhari(int(hari[i]))
            Date.append(textTanggal)
            Imsak.append(textimsak)
            Subuh.append(textsubuh)
            Terbit.append(textterbit)
            Duha.append(textduha)
            Dzuhur.append(textdzuhur)
            Ashar.append(textashar)
            Maghrib.append(textmaghrib)
            Isya.append(textisya)
            i = i + 1
        
        # Fungsi untuk menambahkan data ke tabel
        tree.delete(*tree.get_children())
        for i in range(len(Date)):
            tree.insert("", "end", values=(Date[i], Imsak[i], Subuh[i], Terbit[i], Duha[i], Dzuhur[i], Ashar[i], Maghrib[i], Isya[i]))

    
    #Frame Bawah Map
    frame_bawahmap = customtkinter.CTkFrame(master=frame_right, corner_radius=0, fg_color='transparent')
    frame_bawahmap.grid(row=3, column=0, columnspan=3, pady=0, padx=0, sticky="nsew")

    #Tombol "Set Data"
    button_3 = customtkinter.CTkButton(master=frame_kirimap, text="Set Data", command=set_data)
    button_3.grid(pady=(10, 50), padx=(12, 12), row=15, column=0, sticky='wn')

    #Label Keterangan
    label_keterangan = customtkinter.CTkLabel(frame_bawahmap, text="Prayer Times in : None", font=('',12), anchor="w", justify='left')
    label_keterangan.grid(row=0, column=0, columnspan=3, padx=(12, 12), pady=(0,2), sticky='wn')
        
    # Membuat Treeview (tabel)
    tree = ttk.Treeview(frame_bawahmap, columns=("1", "2", "3", "4", "5", "6", "7", "8", "9" ), show="headings", height=3)

    isi = ["Date (Right Click To Download)", "Imsak", "Subuh", "Rise", "Duha", "Dzuhur", "Ashar", "Maghrib", "Isya"]
    # Menambahkan heading untuk setiap kolom
    i = 0
    for i in range(len(isi)):
        tree.heading(f"{i+1}", text=isi[i], anchor="w")
        tree.column(f"{i+1}", width=40)
        tree.column("1", width=350)
        i + 1

    # Membuat scrollbar
    scrollbar = ttk.Scrollbar(frame_bawahmap, orient="vertical", command=tree.yview)

    # Menyambungkan scrollbar ke tabel
    tree.configure(yscrollcommand=scrollbar.set)

    # Menempatkan tabel dan scrollbar di dalam grid
    tree.grid(row=1, column=0, padx=(12, 0), pady=(2,0), sticky="nsew")
    scrollbar.grid(row=1, column=3, sticky="ns")

    # Mengatur properti grid agar tabel dan scrollbar mengikuti ukuran jendela
    frame_bawahmap.grid_columnconfigure(0, weight=1)

    def export_to_pdf():
    # Mendapatkan data dari Treeview
        data = []
        for item in tree.get_children():
            values = tree.item(item, 'values')
            data.append(values)

        # Menyusun data ke dalam DataFrame
        columns = ["Date", "Imsak", "Subuh", "Rise", "Duha", "Dzuhur", "Ashar", "Maghrib", "Isya"]
        df = pd.DataFrame(data, columns=columns)

        # Memilih lokasi file untuk disimpan
        namafile = f"Prayer Times Program by Ainurriza 2023"
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile= namafile)
        if not file_path:
            return  # Pengguna membatalkan penyimpanan

        # Membuat PDF dengan tata letak yang menarik
        pdf_canvas = canvas.Canvas(file_path, pagesize=letter)
        pdf_canvas.setFont("Helvetica", 10)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Menambahkan gambar sebagai latar belakang full page
        image_path = os.path.join(base_path, "BAHAN.png")
        image = utils.ImageReader(image_path)
        width, height = letter
        pdf_canvas.drawImage(image, 0, 0, width=width, height=height, preserveAspectRatio=True, anchor='sw')


        # Menuliskan judul
        pdf_canvas.drawCentredString(300, 750, f"Monthly {label_keterangan.cget('text')}")
        pdf_canvas.drawCentredString(300, 735, f"Prayer Times Program by Ainurriza 2023")
        pdf_canvas.drawCentredString(300, 720, f"email: muhammadainurriza6@gmail.com")

        # Menuliskan header kolom
        col_widths = [230, 45, 45, 45, 45, 45, 45, 45, 40]  # Menyesuaikan lebar kolom
        col_positions = [20, 250, 295, 340, 385, 430, 475, 520, 565]  # Menyesuaikan posisi kolom

        for col, width, position in zip(columns, col_widths, col_positions):
            pdf_canvas.drawString(position, 700, col)
            pdf_canvas.line(position, 695, position + width, 695)

        # Menuliskan data
        row_height = 20
        for i, row in enumerate(data):
            for value, position in zip(row, col_positions):
                pdf_canvas.drawString(position, 690 - (i + 1) * row_height, str(value))

        # Menyimpan dokumen PDF
        pdf_canvas.save()
        # Menampilkan notifikasi
        notification_title = "Info"
        notification_message = f"The file has been successfully saved to: ({file_path})"
        messagebox.showinfo(notification_title, notification_message)

    def show_context_menu(event):
        # Menampilkan menu kontekstual saat kanan diklik
        context_menu.post(event.x_root, event.y_root)
        
    # Menambahkan opsi menu untuk mencetak ke PDF
    context_menu = tk.Menu(tree, tearoff=0)
    context_menu.add_command(label="Download PDF", command=export_to_pdf)

    # Mengatur event handler untuk klik kanan
    tree.bind("<Button-3>", show_context_menu)
    
    #Keterangan Algoritma
    def algoritma():
        root1 = customtkinter.CTk()
        root1.title("Algoritm")
        root1.geometry(f"{200}x{500}")
        root1.minsize(200, 500)
        root1.geometry(f"+{50}+{50}")
        
        def setting():
            subuhdegree1.append(entry_subuhdegree.get())
            isyadegree1.append(entry_isyadegree.get())
            asharshadow1.append(entry_asharshadow.get())
            correction1.append(entry_correction.get())
            imsaktime1.append(entry_imsaktime.get())
            duhatime1.append(entry_duhatime.get())
            set_data()
            root1.withdraw()

        frame_algoritma = customtkinter.CTkFrame(master=root1, corner_radius=0, fg_color='transparent')
        frame_algoritma.grid(row=0, column=0, pady=0, padx=0, sticky="nsew")
        
        label_subuhdegree = customtkinter.CTkLabel(frame_algoritma, text="Subuh Degree:", anchor="w")
        label_subuhdegree.grid(row=0, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_subuhdegree = customtkinter.CTkOptionMenu(frame_algoritma, values=['-6', '-7', '-8', '-9', '-10', '-11','-12', '-13', '-14', '-15', '-16', '-17', '-18', '-19', '-20'],
                                                           )
        entry_subuhdegree.grid(row=1, column=0, padx=(12, 20), pady=(0),sticky='wn')
        entry_subuhdegree.set(subuhdegree1[-1])

        label_isyadegree = customtkinter.CTkLabel(frame_algoritma, text="Isya Degree:", anchor="w")
        label_isyadegree.grid(row=2, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_isyadegree = customtkinter.CTkOptionMenu(frame_algoritma, values=['-6', '-7', '-8', '-9', '-10', '-11','-12', '-13', '-14', '-15', '-16', '-17', '-18', '-19', '-20'],
                                                           )
        entry_isyadegree.grid(row=3, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_isyadegree.set(isyadegree1[-1])

        label_asharshadow = customtkinter.CTkLabel(frame_algoritma, text="Ashar Shadow:", anchor="w")
        label_asharshadow.grid(row=4, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_asharshadow = customtkinter.CTkOptionMenu(frame_algoritma, values=['1', '2'],
                                                           )
        entry_asharshadow.grid(row=5, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_asharshadow.set(asharshadow1[-1])

        label_correction = customtkinter.CTkLabel(frame_algoritma, text="Correction: ", anchor="w")
        label_correction.grid(row=6, column=0, padx=(12, 0), pady=0, sticky='wn')
        label_correction1 = customtkinter.CTkLabel(frame_algoritma, text="(+ minutes from Prayer Times)", font=('', 11), anchor="w")
        label_correction1.grid(row=7, column=0, padx=(12, 0), pady=0, sticky='wn') 

        entry_correction = customtkinter.CTkOptionMenu(frame_algoritma, values=['0', '1', '2', '3', '4', '5', '6'],
                                                           )
        entry_correction.grid(row=8, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_correction.set(correction1[-1])

        label_imsaktime = customtkinter.CTkLabel(frame_algoritma, text="Imsak Time: ", anchor="w")
        label_imsaktime.grid(row=9, column=0, padx=(12, 0), pady=0, sticky='wn')
        label_imsaktime1 = customtkinter.CTkLabel(frame_algoritma, text="(+ minutes from Subuh Time)", font=('', 11), anchor="w")
        label_imsaktime1.grid(row=10, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_imsaktime = customtkinter.CTkOptionMenu(frame_algoritma, values=['-6', '-7', '-8', '-9', '-10', '-11','-12'],
                                                           )
        entry_imsaktime.grid(row=11, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_imsaktime.set(imsaktime1[-1])

        label_duhatime = customtkinter.CTkLabel(frame_algoritma, text="Duha Time: ", anchor="w")
        label_duhatime.grid(row=12, column=0, padx=(12, 0), pady=0, sticky='wn')
        label_duhatime = customtkinter.CTkLabel(frame_algoritma, text="(+ minutes from Rise Time)", font=('', 11), anchor="w")
        label_duhatime.grid(row=13, column=0, padx=(12, 0), pady=0, sticky='wn')

        entry_duhatime = customtkinter.CTkOptionMenu(frame_algoritma, values=['16', '17', '18', '19', '20', '21', '22', '23', '24'],
                                                           )
        entry_duhatime.grid(row=14, column=0, padx=(12, 20), pady=(0), sticky='wn')
        entry_duhatime.set(duhatime1[-1])

        set_algo = customtkinter.CTkButton(frame_algoritma, text="Set Algoritm", command=setting)
        set_algo.grid(row=15, column=0, padx=(12, 20), pady=(10,0), sticky='wn')
        
        def default():
            entry_subuhdegree.set(-20)
            entry_isyadegree.set(-18)
            entry_asharshadow.set(1)
            entry_correction.set(2)
            entry_imsaktime.set(-10)
            entry_duhatime.set(20)

        set_default = customtkinter.CTkButton(frame_algoritma, text="Default", command=default)
        set_default.grid(row=16, column=0, padx=(12, 20), pady=(5,0), sticky='wn')

        subuhdegree = entry_subuhdegree.get()
        isyadegree = entry_isyadegree.get()
        asharshadow = entry_asharshadow.get()
        correction = entry_correction.get()
        imsaktime = entry_imsaktime.get()
        duhatime = entry_duhatime.get()
        
        def on_focus_out(event):
            root1.withdraw()

        # Menambahkan event handler untuk event FocusOut
        root1.bind('<FocusOut>', on_focus_out)
        
        root1.mainloop()

    algoritma1 = customtkinter.CTkButton(frame_bawahmap, text="Algoritm", command=algoritma, width=10, height=2)
    algoritma1.grid(row=0, column=3, padx=(12, 20), pady=(2,8))

    #Set nilai default
    map_widget.set_position(-7.9526251, 112.6145089) #Posisi Universitas Brawijaya
    map_widget.set_zoom(10)
    map_option_menu.set("OpenStreetMap")

    # Klik kanan untuk menambah lokasi
    map_widget.add_right_click_menu_command(label="Add Location",
                                        command=set_marker_event,
                                        pass_coords=True)    

def about():
    for widget in frame_right.winfo_children():
        widget.destroy()
    set_button_highlight(button_about)
    #Label about
    text1 = '''Program ini dibuat untuk memenuhi tugas matakuliah Komputasi Astronomi pada tahun 2023 Program Studi Fisika Universitas Brawiaya Malang.

Program ini menggunakan algoritma yang sesuai dengan buku karya Dr. Eng. Rinto Anugraha, M.Si. tentang Mekanika Benda Langit.
Dimana setiap tetapan default yang digunakan merujuk pada BUKU SAKU HISAB RUKYAT 2013 - Kementerian Agama Republik Indonesia.

Tetapan default itu diantaranya:
Sudut Subuh      : -20
Sudut Isya       : -18
Waktu Imsak      : - 10 menit Waktu Subuh
Waktu Duha       : + 20 menit Waktu Terbit
Bayangan Ashar   : 1 (panjang bayangan = tinggi benda)

Untuk koreksi waktu maghrib, digunakan ketinggian karena berpengaruh terhadap kapan matahari terlihat terbit dan terbenam.
Jika dirasa koreksi ketinggian ini tidak perlu, pengguna dapat mengganti ketinggian menjadi 0 meter di bagian entry Elevation.

Kemudian untuk kemantaban hati dalam menentukan waktu masuk sholat, program ini secara default menambah 2 menit dari perhitungan.
Jika dirasa penambahan tersebut tidak perlu atau kurang lama, pengguna dapat mengganti pada bagian algoritm beserta menu lainnya.

Untuk current lokasi yang digunakan pada program itu adalah mengikuti lokasi IP pada perangkat yang digunakan bukan GPS.
Harapan kedepannya, program ini dapat dibuat sesuai lokasi GPS yang disediakan.

Silakan hubungi creator program ini jika terdapat beberapa saran dan masukan.
Supervisor:
Dr.rer.nat. Abdurrouf, S.Si, M.Si.
Creator:
Muhammad 'Ainurriza Al Kahfi
email:
muhammadainurriza6@gmail.com
instagram:
@riza_alkahfi

Untuk informasi mengenai materi yang digunakan, silakan kunjungi link berikut:
'''
    label_about1 = customtkinter.CTkLabel(frame_right, text=text1, font=('',14), anchor="w", justify="left")
    label_about1.grid(row=0, column=0, padx=(20, 20), pady=(20,0), sticky='wn')
    
    def open_link(event):
        # Fungsi ini akan dijalankan saat tautan diklik
        import webbrowser
        webbrowser.open("https://drive.google.com/drive/folders/1UHCC_jluJEBWcG5a7-8R_rXI3cKa6DE6?usp=sharing")

    text2 = "https://drive.google.com/drive/folders/1UHCC_jluJEBWcG5a7-8R_rXI3cKa6DE6?usp=sharing"
    label_about2 = ttk.Label(frame_right, text=text2, font=('',14), anchor="w", justify="left", foreground="blue")
    label_about2.grid(row=1, column=0, padx=(20, 20), pady=(0,20), sticky='wn')
    label_about2.bind("<Button-1>", open_link)

# Membuat jendela utama
root = customtkinter.CTk()
root.title("Prayer Times Program by Ainurriza 2023")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.minsize(WIDTH, HEIGHT)
root.geometry(f"+{50}+{50}")

all_buttons = []  # Menyimpan semua tombol

# Frame atas untuk judul
title_frame = customtkinter.CTkFrame(master=root, width=WIDTH, corner_radius=0, fg_color=None)
title_frame.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="nsew")

title_label = customtkinter.CTkLabel(title_frame, text="Prayer Times Program by Ainurriza 2023", fg_color=None)
title_label.pack(expand=True)

# Bagian kiri antarmuka pengguna
frame_left = customtkinter.CTkFrame(master=root, width=150, corner_radius=0, fg_color=None)
frame_left.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

#Tombol Menu Ketiga
button_waktusholat = customtkinter.CTkButton(master=frame_left, text="            Prayer Times           ", command=tombol_waktusholat)
button_waktusholat.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)
all_buttons.append(button_waktusholat)

#Tombol Menu Keempat
button_waktusholat2 = customtkinter.CTkButton(master=frame_left, text="    Monthly Prayer Times   ", command=tombol_monthlyprayer)
button_waktusholat2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)
all_buttons.append(button_waktusholat2)

frame_akhir = customtkinter.CTkFrame(frame_left, corner_radius=0, fg_color='transparent')
frame_akhir.grid(row=4, column=0, padx=(0), pady=(270,0))

button_about = customtkinter.CTkButton(master=frame_akhir, text="               About              ", command=about)
button_about.grid(pady=(20, 20), padx=(20, 20), row=3, column=0)
all_buttons.append(button_about)

# Pilihan "Appearance Mode"
appearance_mode_label = customtkinter.CTkLabel(frame_akhir, text="Appearance Mode:", anchor="w")
appearance_mode_label.grid(row=4, column=0, padx=(20, 20), pady=(0, 0))
appearance_mode_optionemenu = customtkinter.CTkOptionMenu(frame_akhir, values=["Light", "Dark"],
                                                           command=change_appearance_mode)
appearance_mode_optionemenu.grid(row=5, column=0, padx=(20, 20), pady=(0, 10))

label_keterangan = customtkinter.CTkLabel(frame_akhir,
        text='''
Supervisor:
Dr.rer.nat. Abdurrouf, S.Si, M.Si.

Creator:
Muhammad 'Ainurriza Al Kahfi
email:
muhammadainurriza6@gmail.com''', font=("", 10), anchor="w")
label_keterangan.grid(row=6, column=0, padx=(20, 20), pady=(0, 0))

# Bagian kanan antarmuka pengguna
frame_right = customtkinter.CTkFrame(master=root, corner_radius=0)
frame_right.grid(row=1, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

frame_right.grid_rowconfigure(0, weight=0)
frame_right.grid_rowconfigure(1, weight=0)
frame_right.grid_rowconfigure(2, weight=4)
frame_right.grid_rowconfigure(3, weight=9)
frame_right.grid_columnconfigure(0, weight=4)
frame_right.grid_columnconfigure(1, weight=1)
frame_right.grid_columnconfigure(2, weight=0)

appearance_mode_optionemenu.set("Light")
customtkinter.set_appearance_mode("Light")

# Menyesuaikan bobot agar dapat diubah ukurannya dengan benar
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Menjalankan aplikasi
root.mainloop()

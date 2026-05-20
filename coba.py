from flask import Flask, render_template_string, request
from abc import ABC, abstractmethod

app = Flask(__name__)

# ==========================
# CLASS OOP
# ==========================

class PerangkatElektronik(ABC):
    def __init__(self, nama, daya_watt, jam_pakai_per_hari):
        self.nama = nama
        self.daya_watt = daya_watt
        self.jam_pakai_per_hari = jam_pakai_per_hari
        self.__tarif_per_kwh = 1444.70

    def get_tarif_per_kwh(self):
        return self.__tarif_per_kwh

    @abstractmethod
    def hitung_kwh_harian(self):
        pass

    def hitung_kwh_bulanan(self):
        return self.hitung_kwh_harian() * 30

    def hitung_biaya_bulanan(self):
        return self.hitung_kwh_bulanan() * self.get_tarif_per_kwh()


class PerangkatStatis(PerangkatElektronik):
    def hitung_kwh_harian(self):
        return (self.daya_watt * self.jam_pakai_per_hari) / 1000


class PerangkatIntermiten(PerangkatElektronik):
    def hitung_kwh_harian(self):
        return (self.daya_watt * self.jam_pakai_per_hari * 0.95) / 1000


class SistemAnalisisEnergi:
    def __init__(self):
        self.daftar_perangkat = []

    def tambah_perangkat(self, perangkat):
        self.daftar_perangkat.append(perangkat)

    def total_kwh(self):
        return sum(p.hitung_kwh_bulanan() for p in self.daftar_perangkat)

    def total_biaya(self):
        return sum(p.hitung_biaya_bulanan() for p in self.daftar_perangkat)

    def perangkat_paling_boros(self):
        if not self.daftar_perangkat:
            return None
        return max(self.daftar_perangkat, key=lambda p: p.hitung_biaya_bulanan())


# ==========================
# DATA GLOBAL
# ==========================

sistem = SistemAnalisisEnergi()


# ==========================
# HTML TEMPLATE
# ==========================

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sistem Analisis Energi</title>
    <style>
        body {
            font-family: Arial;
            background-color: #f2f2f2;
            padding: 20px;
        }

        h1 {
            color: #333;
        }

        .container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        }

        input, select {
            width: 100%;
            padding: 10px;
            margin-top: 10px;
            margin-bottom: 15px;
        }

        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        table, th, td {
            border: 1px solid #ccc;
        }

        th, td {
            padding: 10px;
            text-align: center;
        }

        .hasil {
            margin-top: 20px;
            background: #eaf7ea;
            padding: 15px;
            border-radius: 10px;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Sistem Analisis Energi Listrik</h1>

    <form method="POST">
        <input type="text" name="nama" placeholder="Nama Perangkat" required>

        <input type="number" step="0.1" name="daya" placeholder="Daya (Watt)" required>

        <input type="number" step="0.1" name="jam" placeholder="Jam Pemakaian per Hari" required>

        <select name="jenis">
            <option value="statis">Perangkat Statis</option>
            <option value="intermiten">Perangkat Intermiten</option>
        </select>

        <button type="submit">Tambah Perangkat</button>
    </form>

    {% if perangkat_list %}

    <table>
        <tr>
            <th>Nama</th>
            <th>Daya</th>
            <th>Jam/Hari</th>
            <th>kWh/Bulan</th>
            <th>Biaya/Bulan</th>
        </tr>

        {% for p in perangkat_list %}
        <tr>
            <td>{{ p.nama }}</td>
            <td>{{ p.daya_watt }} W</td>
            <td>{{ p.jam_pakai_per_hari }} Jam</td>
            <td>{{ '%.2f' % p.hitung_kwh_bulanan() }}</td>
            <td>Rp {{ '{:,.0f}'.format(p.hitung_biaya_bulanan()) }}</td>
        </tr>
        {% endfor %}
    </table>

    <div class="hasil">
        <h3>Total Konsumsi: {{ '%.2f' % total_kwh }} kWh/bulan</h3>
        <h3>Total Tagihan: Rp {{ '{:,.0f}'.format(total_biaya) }}</h3>

        {% if boros %}
        <h3>Perangkat Paling Boros: {{ boros.nama }}</h3>
        {% endif %}
    </div>

    {% endif %}
</div>

</body>
</html>
'''


# ==========================
# ROUTE
# ==========================

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nama = request.form['nama']
        daya = float(request.form['daya'])
        jam = float(request.form['jam'])
        jenis = request.form['jenis']

        if jenis == 'statis':
            perangkat = PerangkatStatis(nama, daya, jam)
        else:
            perangkat = PerangkatIntermiten(nama, daya, jam)

        sistem.tambah_perangkat(perangkat)

    return render_template_string(
        HTML,
        perangkat_list=sistem.daftar_perangkat,
        total_kwh=sistem.total_kwh(),
        total_biaya=sistem.total_biaya(),
        boros=sistem.perangkat_paling_boros()
    )


# ==========================
# RUN APP
# ==========================

if __name__ == '__main__':
    app.run(debug=True)
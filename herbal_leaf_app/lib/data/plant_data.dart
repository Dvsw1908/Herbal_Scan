import '../models/herbal_plant.dart';

const List<HerbalPlant> kHerbalPlants = [
  HerbalPlant(
    name: 'Alpukat',
    latinName: 'Persea americana',
    description:
        'Alpukat adalah buah tropis yang kaya akan nutrisi dan lemak sehat. '
        'Daun alpukat juga dikenal dalam pengobatan tradisional dengan berbagai khasiat '
        'untuk kesehatan tubuh.',
    benefits: [
      'Kaya lemak tak jenuh tunggal (asam oleat) yang baik untuk kesehatan jantung.',
      'Mengandung folat tinggi, sangat bermanfaat bagi ibu hamil untuk perkembangan janin.',
      'Sumber kalium yang membantu mengatur tekanan darah dan fungsi otot.',
      'Mengandung vitamin K, E, C, dan B-kompleks untuk metabolisme tubuh yang optimal.',
      'Memiliki sifat antiinflamasi yang membantu mengurangi peradangan.',
    ],
    iconPath: 'assets/icons/avocado.png',
    leafImagePath: 'assets/leafimage/Daun Alpukat.jpeg',
    usage: [
      'Rebus 5–7 lembar daun alpukat segar dengan 3 gelas air, minum 2× sehari untuk membantu menurunkan tekanan darah.',
      'Seduhan daun alpukat digunakan secara tradisional untuk meredakan nyeri punggung dan rematik.',
      'Ekstrak daun alpukat dimanfaatkan sebagai obat kumur alami untuk menjaga kesehatan mulut.',
    ],
  ),
  HerbalPlant(
    name: 'Srikaya',
    latinName: 'Annona squamosa',
    description:
        'Srikaya adalah buah tropis dengan rasa manis dan tekstur creamy. '
        'Daun dan bijinya telah lama digunakan dalam pengobatan tradisional Asia '
        'untuk berbagai kondisi kesehatan.',
    benefits: [
      'Kaya vitamin C dan antioksidan untuk meningkatkan sistem imunitas tubuh.',
      'Mengandung zat besi yang membantu mencegah dan mengatasi anemia.',
      'Membantu mengontrol kadar gula darah berkat kandungan serat alaminya.',
      'Sumber magnesium yang baik untuk kesehatan otot dan fungsi saraf.',
      'Daun secara tradisional digunakan sebagai antiparasit dan antiseptik alami.',
    ],
    iconPath: 'assets/icons/srikaya.png',
    leafImagePath: 'assets/leafimage/Daun Srikaya.jpg',
    usage: [
      'Tumbuk daun srikaya segar lalu tempelkan pada luka atau bisul sebagai antiseptik alami.',
      'Rebusan daun srikaya digunakan secara tradisional untuk membasmi kutu rambut dan ektoparasit.',
      'Air rebusan daun srikaya diminum untuk membantu menurunkan kadar gula darah pada penderita diabetes.',
    ],
  ),
  HerbalPlant(
    name: 'Salam',
    latinName: 'Syzygium aromaticum',
    description:
        'Salam adalah tanaman yang dikenal dengan aroma harumnya dan memiliki berbagai manfaat kesehatan. Daun salam sering digunakan dalam pengobatan tradisional.',
    benefits: [
      'Mengandung senyawa bioaktif seperti eugenol yang memiliki sifat antiinflamasi dan antimikroba.',
      'Membantu mengurangi gejala maag dan gangguan pencernaan.',
      'Memiliki efek relaksan otot dan dapat membantu mengurangi nyeri otot.',
      'Mengandung antioksidan yang membantu melindungi sel-sel tubuh dari kerusakan.',
      'Dapat membantu menurunkan kadar gula darah secara alami.',
    ],
    iconPath: 'assets/icons/bay.png',
    leafImagePath: 'assets/leafimage/Daun Salam.jpeg',
    usage: [
      'Rebus 5–7 lembar daun salam dengan 3 gelas air, minum 2× sehari untuk mengatasi maag dan gangguan pencernaan.',
      'Daun salam dapat digunakan sebagai obat alami untuk meredakan nyeri otot dan sendi.',
      'Ekstrak daun salam dimanfaatkan sebagai antiseptik alami untuk menjaga kesehatan mulut.',
    ],
  ),
  HerbalPlant(
    name: 'Leci',
    latinName: 'Litchi chinensis',
    description:
        'Leci adalah buah tropis asal Cina yang kini banyak dibudidayakan di Asia Tenggara. '
        'Buahnya yang manis dan menyegarkan mengandung berbagai senyawa bioaktif bermanfaat.',
    benefits: [
      'Sangat kaya vitamin C — satu sajian memenuhi lebih dari 100% kebutuhan harian.',
      'Mengandung oligonol (senyawa polifenol) yang memiliki efek anti-penuaan.',
      'Membantu meningkatkan sirkulasi darah dan kesehatan sistem kardiovaskular.',
      'Sumber kalium alami yang mendukung fungsi jantung dan keseimbangan cairan.',
      'Mengandung quercetin dengan sifat antiinflamasi dan antihistamin alami.',
    ],
    iconPath: 'assets/icons/lychee.png',
    leafImagePath: 'assets/leafimage/Daun Leci.jpeg',
    usage: [
      'Konsumsi buah leci segar secara rutin untuk meningkatkan stamina dan daya tahan tubuh.',
      'Ekstrak daun leci digunakan dalam pengobatan tradisional Tiongkok untuk mengatasi batuk dan diare.',
      'Biji leci yang dihaluskan dimanfaatkan sebagai pereda nyeri pada gangguan pencernaan.',
    ],
  ),
  HerbalPlant(
    name: 'Belimbing Wuluh',
    latinName: 'Averrhoa bilimbi',
    description:
        'Belimbing wuluh adalah tanaman asli Maluku yang kini tersebar luas di Asia Tenggara. '
        'Buahnya yang asam banyak digunakan sebagai bumbu masakan dan obat tradisional.',
    benefits: [
      'Kaya vitamin C untuk meningkatkan daya tahan tubuh terhadap infeksi.',
      'Membantu menurunkan tekanan darah tinggi (hipertensi) secara alami.',
      'Memiliki efek antimikroba dan antiinflamasi yang telah terbukti secara ilmiah.',
      'Secara tradisional digunakan untuk membantu mengelola kadar gula darah.',
      'Membantu meredakan batuk dan infeksi pada saluran pernapasan.',
    ],
    iconPath: 'assets/icons/starfruit.png',
    leafImagePath: 'assets/leafimage/Daun Belimbing Wuluh.jpeg',
    usage: [
      'Rebus buah belimbing wuluh dengan gula batu, minum 2× sehari untuk meredakan batuk berdahak.',
      'Tumbuk daun belimbing wuluh lalu oleskan pada kulit yang terkena jerawat atau panu.',
      'Sari buah belimbing wuluh diminum untuk membantu menurunkan tekanan darah tinggi secara alami.',
    ],
  ),
  HerbalPlant(
    name: 'Nangka',
    latinName: 'Artocarpus heterophyllus',
    description:
        'Nangka adalah buah tropis terbesar di dunia yang banyak ditemukan di Asia Selatan '
        'dan Tenggara. Selain buahnya, daun nangka juga memiliki manfaat kesehatan.',
    benefits: [
      'Kaya serat pangan yang menjaga kesehatan dan kelancaran pencernaan.',
      'Mengandung vitamin B6 untuk mendukung kesehatan otak dan metabolisme energi.',
      'Sumber kalium yang membantu mengontrol tekanan darah secara alami.',
      'Mengandung antioksidan flavonoid dan karotenoid pelindung sel dari kerusakan.',
      'Indeks glikemik rendah sehingga baik dikonsumsi oleh penderita diabetes.',
    ],
    iconPath: 'assets/icons/jackfruit.png',
    leafImagePath: 'assets/leafimage/Daun Nangka.jpeg',
    usage: [
      'Rebus 3–5 lembar daun nangka muda, minum air rebusannya untuk membantu mengontrol gula darah.',
      'Daun nangka yang dihaluskan digunakan sebagai obat oles tradisional untuk mempercepat penyembuhan luka.',
      'Teh daun nangka dikonsumsi secara rutin untuk menjaga kesehatan pencernaan dan mengurangi sembelit.',
    ],
  ),
  HerbalPlant(
    name: 'Jambu Biji',
    latinName: 'Psidium guajava',
    description:
        'Jambu biji adalah buah tropis yang tumbuh subur di daerah hangat. '
        'Kandungan vitamin C-nya yang luar biasa tinggi menjadikannya salah satu '
        'buah paling bergizi di dunia.',
    benefits: [
      'Kandungan vitamin C 4× lebih tinggi dari jeruk — terbaik untuk imunitas tubuh.',
      'Membantu melawan infeksi bakteri dan virus berkat sifat antimikrobanya.',
      'Mengandung likopen yang mendukung kesehatan kulit dan bersifat anti-kanker.',
      'Serat tinggi mendukung kesehatan usus dan mencegah sembelit.',
      'Membantu mengontrol kadar gula darah dan kolesterol secara alami.',
    ],
    iconPath: 'assets/icons/guava.png',
    leafImagePath: 'assets/leafimage/Daun Jambu Biji.jpg',
    usage: [
      'Rebus 8–10 lembar daun jambu biji muda, minum 3× sehari untuk mengatasi diare dan disentri.',
      'Kunyah daun jambu biji segar atau gunakan air rebusannya sebagai obat kumur untuk meredakan sakit gigi.',
      'Oleskan pasta daun jambu biji yang ditumbuk pada luka untuk mempercepat penyembuhan dan mencegah infeksi.',
    ],
  ),
  HerbalPlant(
    name: 'Sirsak',
    latinName: 'Annona muricata',
    description:
        'Sirsak adalah buah tropis dengan rasa manis-asam yang khas. Tanaman ini '
        'dikenal luas dalam pengobatan tradisional dan menjadi subjek penelitian ilmiah '
        'karena kandungan bioaktifnya yang unik.',
    benefits: [
      'Mengandung senyawa acetogenin yang menunjukkan sifat antiproliferatif dalam riset.',
      'Kaya antioksidan untuk melindungi sel-sel tubuh dari kerusakan radikal bebas.',
      'Memiliki sifat antiinflamasi dan antimikroba yang membantu melawan infeksi.',
      'Secara tradisional digunakan untuk mengatasi insomnia dan menenangkan saraf.',
      'Membantu memperkuat sistem imun tubuh secara keseluruhan.',
    ],
    iconPath: 'assets/icons/soursop.png',
    leafImagePath: 'assets/leafimage/Daun Sirsak.jpg',
    usage: [
      'Rebus 10 lembar daun sirsak dengan 3 gelas air hingga tersisa 1 gelas, minum 1× sehari untuk menjaga imunitas.',
      'Teh daun sirsak diminum menjelang tidur untuk membantu mengatasi insomnia dan menenangkan sistem saraf.',
      'Tempelkan daun sirsak yang dihangatkan pada area nyeri sendi atau rematik sebagai terapi topikal tradisional.',
    ],
  ),
];

HerbalPlant? findPlant(String predictedClassName) {
  // Strip "Daun " prefix so "Daun Belimbing Wuluh" matches "Belimbing Wuluh"
  final normalized = predictedClassName
      .replaceFirst(RegExp(r'^Daun\s+', caseSensitive: false), '')
      .replaceAll(RegExp(r'\s+Rusak', caseSensitive: false), '')
      .replaceAll(RegExp(r'\s+(NoBG|BG)\s*$', caseSensitive: false), '')
      .trim()
      .toLowerCase();
  try {
    return kHerbalPlants.firstWhere((p) => p.name.toLowerCase() == normalized);
  } catch (_) {
    return null;
  }
}

import 'package:flutter/material.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8F3),
      appBar: AppBar(title: const Text('Pengaturan')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _SectionHeader(label: 'Bantuan'),
          _SettingItem(
            icon: Icons.help_outline,
            title: 'Cara Menggunakan',
            subtitle: 'Panduan penggunaan HerbalScan',
            onTap: () => _showTutorialDialog(context),
          ),
          _SettingItem(
            icon: Icons.menu_book,
            title: 'Tentang Dataset',
            subtitle: '16 kelas daun herbal (sehat & rusak)',
            onTap: () => _showDatasetInfo(context),
          ),
          const SizedBox(height: 12),
          _SectionHeader(label: 'Informasi'),
          _SettingItem(
            icon: Icons.info_outline,
            title: 'Tentang Aplikasi',
            subtitle: 'HerbalScan v1.0.0',
            onTap: () => _showAboutDialog(context),
          ),
          _SettingItem(
            icon: Icons.science_outlined,
            title: 'Model AI',
            subtitle: 'ShuffleNetV2 — PyTorch',
            onTap: () => _showModelInfo(context),
          ),
        ],
      ),
    );
  }

  void _showTutorialDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Cara Menggunakan HerbalScan'),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _Step(
                number: '1',
                text: 'Buka halaman Home dan tekan tombol "Pilih Gambar".',
              ),
              _Step(
                number: '2',
                text: 'Pilih sumber gambar: Kamera (foto langsung) atau Galeri.',
              ),
              _Step(
                number: '3',
                text: 'Pastikan daun terlihat jelas, pencahayaan cukup, dan latar tidak terlalu ramai.',
              ),
              _Step(
                number: '4',
                text: 'Tunggu hasil prediksi. Aplikasi akan menampilkan nama daun dan tingkat keyakinan model.',
              ),
              _Step(
                number: '5',
                text: 'Hasil otomatis tersimpan di riwayat.',
              ),
            ],
          ),
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Mengerti'),
          ),
        ],
      ),
    );
  }

  void _showDatasetInfo(BuildContext context) {
    const classes = [
      'Daun Alpukat', 'Daun Belimbing Wuluh', 'Daun Jambu Biji', 'Daun Leci',
      'Daun Mangga', 'Daun Nangka', 'Daun Sirsak', 'Daun Srikaya',
    ];
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Informasi Dataset'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                '16 kelas total:\n8 spesies × (sehat + rusak)',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              ...classes.map((c) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Row(
                      children: [
                        Icon(Icons.local_florist,
                            size: 16, color: Theme.of(context).colorScheme.primary),
                        const SizedBox(width: 6),
                        Text(c),
                      ],
                    ),
                  )),
            ],
          ),
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tutup'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showAboutDialog(
      context: context,
      applicationName: 'HerbalScan',
      applicationVersion: '1.0.0',
      applicationLegalese: '© 2025 — Skripsi Klasifikasi Daun Herbal',
      children: const [
        SizedBox(height: 12),
        Text(
          'HerbalScan adalah aplikasi mobile berbasis AI untuk mengklasifikasikan '
          'jenis dan kondisi daun tanaman herbal menggunakan model deep learning '
          'ShuffleNetV2.',
        ),
      ],
    );
  }

  void _showModelInfo(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Informasi Model AI'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _InfoRow(label: 'Arsitektur', value: 'ShuffleNetV2 x1.0'),
            _InfoRow(label: 'Framework', value: 'PyTorch'),
            _InfoRow(label: 'Input', value: '224 × 224 piksel'),
            _InfoRow(label: 'Kelas', value: '16 (8 spesies × 2 kondisi)'),
            _InfoRow(label: 'Preprocessing', value: 'Remove BG (rembg) + Resize'),
            _InfoRow(label: 'Backend', value: 'FastAPI (REST API)'),
          ],
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tutup'),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String label;
  const _SectionHeader({required this.label});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Text(
        label.toUpperCase(),
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: Theme.of(context).colorScheme.outline,
              letterSpacing: 1.2,
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }
}

class _SettingItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;

  const _SettingItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.primaryContainer,
          child: Icon(icon, color: Theme.of(context).colorScheme.primary),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
}

class _Step extends StatelessWidget {
  final String number;
  final String text;
  const _Step({required this.number, required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 11,
            backgroundColor: Theme.of(context).colorScheme.primary,
            child: Text(
              number,
              style: const TextStyle(color: Colors.white, fontSize: 11),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
            ),
          ),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 13))),
        ],
      ),
    );
  }
}

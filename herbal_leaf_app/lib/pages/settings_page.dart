import 'package:flutter/material.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F7F4),
      body: Column(
        children: [
          _SettingsHeader(),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
              children: [
                _SectionLabel(label: 'Bantuan'),
                const SizedBox(height: 10),
                _SettingCard(
                  icon: Icons.help_outline_rounded,
                  iconColor: const Color(0xFF1F6F43),
                  title: 'Cara Menggunakan',
                  subtitle: 'Panduan penggunaan HerbalScan',
                  onTap: () => _showTutorialDialog(context),
                ),
                const SizedBox(height: 10),
                _SettingCard(
                  icon: Icons.menu_book_rounded,
                  iconColor: const Color(0xFF1565C0),
                  title: 'Tentang Dataset',
                  subtitle: '16 kelas daun herbal (sehat & rusak)',
                  onTap: () => _showDatasetInfo(context),
                ),
                const SizedBox(height: 24),
                _SectionLabel(label: 'Informasi'),
                const SizedBox(height: 10),
                _SettingCard(
                  icon: Icons.info_outline_rounded,
                  iconColor: const Color(0xFFB06A00),
                  title: 'Tentang Aplikasi',
                  subtitle: 'HerbalScan v1.0.0',
                  onTap: () => _showAboutDialog(context),
                ),
                const SizedBox(height: 10),
                _SettingCard(
                  icon: Icons.science_outlined,
                  iconColor: const Color(0xFF7B1FA2),
                  title: 'Model AI',
                  subtitle: 'ShuffleNetV2 — PyTorch',
                  onTap: () => _showModelInfo(context),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showTutorialDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: const Text(
          'Cara Menggunakan HerbalScan',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _Step(
                number: '1',
                text: 'Buka halaman Home dan tekan tombol "Scan Daun Herbal".',
              ),
              _Step(
                number: '2',
                text:
                    'Pilih sumber gambar: Kamera (foto langsung) atau Galeri.',
              ),
              _Step(
                number: '3',
                text:
                    'Pastikan daun terlihat jelas, tidak boleh terlipat, pencahayaan cukup, dan latar tidak terlalu ramai.',
              ),
              _Step(
                number: '4',
                text:
                    'Tunggu hasil prediksi. Aplikasi akan menampilkan nama daun dan tingkat keyakinan model.',
              ),
              _Step(number: '5', text: 'Hasil otomatis tersimpan di riwayat.'),
            ],
          ),
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(context),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF1F6F43),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text('Mengerti'),
          ),
        ],
      ),
    );
  }

  void _showDatasetInfo(BuildContext context) {
    const classes = [
      'Daun Alpukat',
      'Daun Belimbing Wuluh',
      'Daun Jambu Biji',
      'Daun Leci',
      'Daun Salam',
      'Daun Nangka',
      'Daun Sirsak',
      'Daun Srikaya',
    ];
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: const Text(
          'Informasi Dataset',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFEAF3EC),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Row(
                  children: [
                    Icon(
                      Icons.info_rounded,
                      color: Color(0xFF1F6F43),
                      size: 18,
                    ),
                    SizedBox(width: 8),
                    Text(
                      '16 kelas: 8 spesies × (sehat + rusak)',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1F6F43),
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              ...classes.map(
                (c) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.local_florist_rounded,
                        size: 15,
                        color: Color(0xFF1F6F43),
                      ),
                      const SizedBox(width: 8),
                      Text(c, style: const TextStyle(fontSize: 13)),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(context),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF1F6F43),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
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
          style: TextStyle(fontSize: 13, height: 1.5),
        ),
      ],
    );
  }

  void _showModelInfo(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: const Text(
          'Informasi Model AI',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _InfoRow(label: 'Arsitektur', value: 'ShuffleNetV2 x1.0'),
            _InfoRow(label: 'Framework', value: 'PyTorch'),
            _InfoRow(label: 'Input', value: '224 × 224 piksel'),
            _InfoRow(label: 'Kelas', value: '16 (8 spesies × 2 kondisi)'),
            _InfoRow(
              label: 'Preprocessing',
              value: 'Remove BG (rembg) + Resize',
            ),
            _InfoRow(label: 'Backend', value: 'FastAPI (REST API)'),
          ],
        ),
        actions: [
          FilledButton(
            onPressed: () => Navigator.pop(context),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF1F6F43),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text('Tutup'),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Header
// ─────────────────────────────────────────────────────────────────────────────
class _SettingsHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final topPad = MediaQuery.of(context).padding.top;
    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0D3D22), Color(0xFF1B5E38), Color(0xFF2E9B61)],
        ),
      ),
      child: Padding(
        padding: EdgeInsets.fromLTRB(24, topPad + 18, 24, 28),
        child: Row(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.18),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: Colors.white.withValues(alpha: 0.25),
                  width: 1.5,
                ),
              ),
              child: const Icon(
                Icons.settings_rounded,
                color: Colors.white,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Pengaturan',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: -0.3,
                  ),
                ),
                Text(
                  'HerbalScan v1.0.0',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Section label
// ─────────────────────────────────────────────────────────────────────────────
class _SectionLabel extends StatelessWidget {
  final String label;
  const _SectionLabel({required this.label});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        label.toUpperCase(),
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: Color(0xFF6B7B8E),
          letterSpacing: 1.4,
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Setting card
// ─────────────────────────────────────────────────────────────────────────────
class _SettingCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;

  const _SettingCard({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(18),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              child: Row(
                children: [
                  Container(
                    width: 46,
                    height: 46,
                    decoration: BoxDecoration(
                      color: iconColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Icon(icon, color: iconColor, size: 24),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                            color: Color(0xFF1A1A2E),
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          subtitle,
                          style: const TextStyle(
                            fontSize: 12,
                            color: Color(0xFF6B7B8E),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    Icons.arrow_forward_ios_rounded,
                    size: 15,
                    color: Colors.grey.shade400,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Dialog widgets
// ─────────────────────────────────────────────────────────────────────────────
class _Step extends StatelessWidget {
  final String number;
  final String text;
  const _Step({required this.number, required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 26,
            height: 26,
            decoration: const BoxDecoration(
              color: Color(0xFF1F6F43),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                number,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(fontSize: 13, height: 1.5),
            ),
          ),
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
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 13,
                color: Color(0xFF1A1A2E),
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontSize: 13, color: Color(0xFF6B7B8E)),
            ),
          ),
        ],
      ),
    );
  }
}

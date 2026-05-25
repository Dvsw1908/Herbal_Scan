import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../providers/prediction_provider.dart';
import '../models/prediction.dart';
import '../data/plant_data.dart';
import '../widgets/stat_card.dart';
import '../widgets/plant_card.dart';
import 'result_page.dart';
import 'batch_result_page.dart';
import 'plant_detail_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulseCtrl;
  late final Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(
      begin: 1.0,
      end: 1.05,
    ).animate(CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickMultiAndPredict(BuildContext context) async {
    final picker = ImagePicker();
    final picked = await picker.pickMultiImage(imageQuality: 85, maxWidth: 1024);
    if (picked.isEmpty) return;
    if (!context.mounted) return;

    final files = picked.map((x) => File(x.path)).toList();
    final provider = context.read<PredictionProvider>();

    // Show progress dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => _BatchProgressDialog(provider: provider, total: files.length),
    );

    final results = await provider.predictBatch(files);

    if (!context.mounted) return;
    Navigator.pop(context); // close dialog

    if (provider.state == PredictionState.error) {
      _showErrorSnackbar(context, provider.errorMessage ?? 'Terjadi kesalahan.');
      return;
    }

    if (results.length == 1) {
      _showResult(context, results.first, files.first);
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => BatchResultPage(results: results)),
    );
  }

  Future<void> _pickAndPredict(BuildContext context, ImageSource source) async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(
      source: source,
      imageQuality: 85,
      maxWidth: 1024,
    );
    if (picked == null) return;
    if (!context.mounted) return;

    await context.read<PredictionProvider>().predictImage(File(picked.path));

    if (!context.mounted) return;

    final provider = context.read<PredictionProvider>();
    if (provider.state == PredictionState.success &&
        provider.lastResult != null) {
      _showResult(context, provider.lastResult!, File(picked.path));
    } else if (provider.state == PredictionState.error) {
      _showErrorSnackbar(
        context,
        provider.errorMessage ?? 'Terjadi kesalahan.',
      );
    }
  }

  void _showSourceSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (ctx) => Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 28),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 14),
                Container(
                  width: 44,
                  height: 5,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
                const SizedBox(height: 28),
                Row(
                  children: [
                    Container(
                      width: 42,
                      height: 42,
                      decoration: BoxDecoration(
                        color: const Color(0xFFEAF3EC),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(
                        Icons.add_a_photo_rounded,
                        color: Color(0xFF1F6F43),
                        size: 22,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Pilih Sumber Gambar',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1A1A2E),
                          ),
                        ),
                        Text(
                          'Foto langsung atau pilih dari galeri',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey.shade500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 28),
                Row(
                  children: [
                    Expanded(
                      child: _SourceOption(
                        icon: Icons.camera_alt_rounded,
                        label: 'Kamera',
                        sublabel: 'Foto langsung',
                        color: const Color(0xFF1F6F43),
                        onTap: () {
                          Navigator.pop(ctx);
                          _pickAndPredict(context, ImageSource.camera);
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _SourceOption(
                        icon: Icons.photo_library_rounded,
                        label: 'Galeri',
                        sublabel: 'Dari penyimpanan',
                        color: const Color(0xFF1565C0),
                        onTap: () {
                          Navigator.pop(ctx);
                          _pickAndPredict(context, ImageSource.gallery);
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: _SourceOption(
                        icon: Icons.photo_library_rounded,
                        label: 'Banyak Foto',
                        sublabel: 'Batch dari galeri',
                        color: const Color(0xFF6A1B9A),
                        onTap: () {
                          Navigator.pop(ctx);
                          _pickMultiAndPredict(context);
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 36),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showResult(BuildContext context, Prediction result, File imageFile) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ResultPage(result: result, imageFile: imageFile),
      ),
    );
  }

  void _showErrorSnackbar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.white, size: 18),
            const SizedBox(width: 10),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: Colors.red.shade700,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F7F4),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _HeroHeader(),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Consumer<PredictionProvider>(
                    builder: (context, provider, _) =>
                        _buildStatsRow(context, provider),
                  ),
                  const SizedBox(height: 24),
                  Consumer<PredictionProvider>(
                    builder: (context, provider, _) => _buildScanCard(
                      context,
                      provider.state == PredictionState.loading,
                    ),
                  ),
                  const SizedBox(height: 32),
                  _buildSectionLabel(context),
                  const SizedBox(height: 16),
                  _buildPlantGrid(context),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsRow(BuildContext context, PredictionProvider provider) {
    return Row(
      children: [
        Expanded(
          child: StatCard(
            icon: Icons.local_florist_rounded,
            title: 'Jenis Daun',
            value: '${kHerbalPlants.length}',
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF1B5E38), Color(0xFF2E9B61)],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: StatCard(
            icon: Icons.verified_rounded,
            title: 'Akurasi',
            value: '~98%',
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFFB06A00), Color(0xFFE8A020)],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: StatCard(
            icon: Icons.history_rounded,
            title: 'Riwayat',
            value: provider.state == PredictionState.loading
                ? '-'
                : '${provider.history.length}',
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF1565C0), Color(0xFF42A5F5)],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildScanCard(BuildContext context, bool isLoading) {
    return AnimatedBuilder(
      animation: _pulseAnim,
      builder: (context, child) => Transform.scale(
        scale: isLoading ? 1.0 : _pulseAnim.value,
        child: child,
      ),
      child: GestureDetector(
        onTap: isLoading ? null : () => _showSourceSheet(context),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 36, horizontal: 28),
          decoration: BoxDecoration(
            gradient: isLoading
                ? LinearGradient(
                    colors: [Colors.grey.shade500, Colors.grey.shade600],
                  )
                : const LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(0xFF0D3D22),
                      Color(0xFF1B5E38),
                      Color(0xFF2A8A55),
                    ],
                  ),
            borderRadius: BorderRadius.circular(28),
            boxShadow: [
              BoxShadow(
                color: (isLoading ? Colors.grey : const Color(0xFF1F6F43))
                    .withValues(alpha: 0.42),
                blurRadius: 28,
                offset: const Offset(0, 12),
              ),
            ],
          ),
          child: Column(
            children: [
              Container(
                width: 88,
                height: 88,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.16),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.28),
                    width: 2,
                  ),
                ),
                child: Center(
                  child: isLoading
                      ? const SizedBox(
                          width: 34,
                          height: 34,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2.5,
                          ),
                        )
                      : const Icon(
                          Icons.camera_alt_rounded,
                          color: Colors.white,
                          size: 44,
                        ),
                ),
              ),
              const SizedBox(height: 18),
              Text(
                isLoading ? 'Menganalisis Daun...' : 'Scan Daun Herbal',
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: 0.2,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                isLoading
                    ? 'Model AI sedang memproses gambar Anda'
                    : 'Identifikasi jenis dan kondisi daun secara instan',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white.withValues(alpha: 0.78),
                  fontSize: 13,
                  height: 1.45,
                ),
              ),
              if (!isLoading) ...[
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _ActionChip(
                      icon: Icons.camera_alt_rounded,
                      label: 'Kamera',
                    ),
                    const SizedBox(width: 12),
                    _ActionChip(
                      icon: Icons.photo_library_rounded,
                      label: 'Galeri',
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionLabel(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Database Tanaman Herbal',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1A1A2E),
              ),
            ),
            Text(
              '${kHerbalPlants.length} spesies tersedia',
              style: const TextStyle(fontSize: 13, color: Color(0xFF6B7B8E)),
            ),
          ],
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: const Color(0xFFEAF3EC),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Text(
            'Semua',
            style: TextStyle(
              fontSize: 12,
              color: Color(0xFF1F6F43),
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPlantGrid(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final crossAxisCount = constraints.maxWidth > 500 ? 3 : 2;
        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount,
            mainAxisSpacing: 14,
            crossAxisSpacing: 14,
            childAspectRatio: 0.95,
          ),
          itemCount: kHerbalPlants.length,
          itemBuilder: (_, i) {
            final plant = kHerbalPlants[i];
            return PlantCard(
              name: plant.name,
              latin: plant.latinName,
              iconPath: plant.iconPath,
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => PlantDetailPage(plant: plant),
                ),
              ),
            );
          },
        );
      },
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Hero header
// ─────────────────────────────────────────────────────────────────────────────
class _HeroHeader extends StatelessWidget {
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
        padding: EdgeInsets.fromLTRB(24, topPad + 18, 24, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.16),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: Colors.white.withValues(alpha: 0.25),
                          width: 1.5,
                        ),
                      ),
                      child: const Icon(
                        Icons.eco_rounded,
                        color: Colors.white,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 12),
                    const Text(
                      'HerbalScan',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.4,
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: Colors.white.withValues(alpha: 0.25),
                    ),
                  ),
                  child: const Text(
                    'v1.0.0',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 26),
            const Text(
              'Identifikasi\nDaun Herbal',
              style: TextStyle(
                color: Colors.white,
                fontSize: 34,
                fontWeight: FontWeight.bold,
                height: 1.15,
                letterSpacing: -0.5,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              'Didukung teknologi ShuffleNetV2 AI',
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.72),
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Bottom sheet source option button
// ─────────────────────────────────────────────────────────────────────────────
class _SourceOption extends StatelessWidget {
  final IconData icon;
  final String label;
  final String sublabel;
  final Color color;
  final VoidCallback onTap;

  const _SourceOption({
    required this.icon,
    required this.label,
    required this.sublabel,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color.withValues(alpha: 0.08),
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        splashColor: color.withValues(alpha: 0.15),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 30),
              ),
              const SizedBox(height: 12),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                ),
              ),
              const SizedBox(height: 3),
              Text(
                sublabel,
                style: TextStyle(
                  color: color.withValues(alpha: 0.7),
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Batch progress dialog
// ─────────────────────────────────────────────────────────────────────────────
class _BatchProgressDialog extends StatelessWidget {
  final PredictionProvider provider;
  final int total;

  const _BatchProgressDialog({required this.provider, required this.total});

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      child: Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: ListenableBuilder(
            listenable: provider,
            builder: (_, _) {
              final done = provider.batchDone;
              final t = provider.batchTotal;
              final progress = t == 0 ? 0.0 : done / t;
              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.auto_awesome_rounded,
                      color: Color(0xFF1F6F43), size: 40),
                  const SizedBox(height: 16),
                  const Text(
                    'Memproses Gambar',
                    style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1A1A2E)),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '$done dari $t gambar',
                    style: const TextStyle(
                        fontSize: 13, color: Color(0xFF6B7B8E)),
                  ),
                  const SizedBox(height: 20),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 10,
                      backgroundColor: const Color(0xFFEAF3EC),
                      valueColor: const AlwaysStoppedAnimation(Color(0xFF1F6F43)),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${(progress * 100).toStringAsFixed(0)}%',
                    style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1F6F43)),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Scan card action chips
// ─────────────────────────────────────────────────────────────────────────────
class _ActionChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _ActionChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.18),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withValues(alpha: 0.32)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.white, size: 14),
          const SizedBox(width: 6),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

class HerbalPlant {
  final String name;
  final String latinName;
  final String description;
  final List<String> benefits;
  final String iconPath;
  final String leafImagePath;
  final List<String> usage;

  const HerbalPlant({
    required this.name,
    required this.latinName,
    required this.description,
    required this.benefits,
    required this.iconPath,
    required this.leafImagePath,
    required this.usage,
  });
}

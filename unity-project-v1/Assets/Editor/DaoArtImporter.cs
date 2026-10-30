using System.IO;
using UnityEditor;
using UnityEngine;

namespace YifuArt.Editor
{
    public sealed class DaoArtImporter : AssetPostprocessor
    {
        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith("Assets/Resources/DaoArt/")) return;
            var catalog = JsonUtility.FromJson<CatalogData>(File.ReadAllText("Assets/Resources/DaoArtCatalog.json"));
            string id = Path.GetFileNameWithoutExtension(assetPath);
            foreach (var row in catalog.assets)
            {
                if (row.id != id) continue;
                var importer = (TextureImporter)assetImporter;
                importer.textureType = row.textureOnly ? TextureImporterType.Default : TextureImporterType.Sprite;
                importer.spriteImportMode = SpriteImportMode.Single;
                importer.spritePixelsPerUnit = 128;
                importer.mipmapEnabled = false;
                importer.isReadable = false;
                importer.alphaIsTransparency = !row.textureOnly;
                importer.sRGBTexture = row.id != "env_repeat_noise";
                importer.npotScale = TextureImporterNPOTScale.None;
                importer.filterMode = FilterMode.Bilinear;
                importer.wrapMode = row.textureOnly ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.maxTextureSize = 4096;
                if (!row.textureOnly)
                {
                    var settings = new TextureImporterSettings();
                    importer.ReadTextureSettings(settings);
                    settings.spriteAlignment = (int)SpriteAlignment.Custom;
                    settings.spritePivot = new Vector2(row.pivot[0], row.pivot[1]);
                    settings.spriteBorder = new Vector4(row.border[0], row.border[1], row.border[2], row.border[3]);
                    settings.spriteMeshType = SpriteMeshType.FullRect;
                    importer.SetTextureSettings(settings);
                }
                break;
            }
        }
    }
}

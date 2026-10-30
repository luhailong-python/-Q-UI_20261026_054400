using System;
using System.Collections.Generic;
using UnityEngine;

namespace YifuArt
{
    [Serializable] public sealed class ArtRow
    {
        public string id, resource, sourceSha256, kind;
        public float[] pivot, border;
        public bool textureOnly;
        public int width, height;
    }
    [Serializable] public sealed class ActorRow
    {
        public string id, name, staticArt;
        public string[] frames;
        public float[] seconds;
        public float displayHeight, staticVisibleHeightPx;
        public bool floating;
    }
    [Serializable] public sealed class CatalogData
    {
        public string gameName;
        public ArtRow[] assets;
        public ActorRow[] actors;
    }
    public static class ArtCatalog
    {
        private static CatalogData data;
        private static Dictionary<string, Sprite> sprites = new Dictionary<string, Sprite>();
        public static CatalogData Data
        {
            get
            {
                if (data == null)
                {
                    var json = Resources.Load<TextAsset>("DaoArtCatalog");
                    if (json == null) throw new InvalidOperationException("Missing DaoArtCatalog.json");
                    data = JsonUtility.FromJson<CatalogData>(json.text);
                }
                return data;
            }
        }
        public static Sprite Sprite(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            if (sprites.TryGetValue(id, out var cached)) return cached;
            foreach (var row in Data.assets)
                if (row.id == id)
                {
                    var result = Resources.Load<Sprite>(row.resource);
                    if (result == null) throw new InvalidOperationException("Sprite not imported: " + id);
                    sprites[id] = result;
                    return result;
                }
            throw new KeyNotFoundException(id);
        }
        public static ActorRow Actor(string id)
        {
            foreach (var row in Data.actors) if (row.id == id) return row;
            throw new KeyNotFoundException(id);
        }
        public static Texture2D Texture(string id)
        {
            foreach (var row in Data.assets)
                if (row.id == id) return Resources.Load<Texture2D>(row.resource);
            return null;
        }
    }
}

using System;
using System.IO;
using System.Linq;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
class Program
{
    static int Main(string[] args)
    {
        var files = Directory.GetFiles(args[0], "*.cs", SearchOption.AllDirectories);
        var errors = files.SelectMany(path => CSharpSyntaxTree.ParseText(File.ReadAllText(path), path: path).GetDiagnostics())
            .Where(d => d.Severity == DiagnosticSeverity.Error).Select(d => d.ToString()).ToArray();
        Console.WriteLine(System.Text.Json.JsonSerializer.Serialize(new { checkedCSharpFiles = files.Length, syntaxErrors = errors, unityCompilationVerified = false, note = "Roslyn syntax only; actual Unity Editor API/type/import/playback validation still required." }));
        return errors.Length == 0 ? 0 : 1;
    }
}

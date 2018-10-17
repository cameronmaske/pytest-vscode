"use strict";
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import cp = require("child_process");
import { parse, shouldSuggest } from "./parse";
import path = require("path");

export const PYTHON: vscode.DocumentFilter = {
  language: "python",
  scheme: "file"
};

const fixtureSuggestions = filepath => {
  return new Promise<any[]>((resolve, reject) => {
    // TODO: Make this configurable
    const args = ["run", "pytest", "-q", "--fixtures", filepath];
    let p = cp.spawn("pipenv", args, {
      cwd: vscode.workspace.rootPath
    });

    console.log(`Running ${args} in ${vscode.workspace.rootPath}`);

    let stdout = "";
    let stderr = "";

    p.stdout.on("data", data => {
      stdout += data;
    });
    p.stderr.on("data", data => {
      stderr += data;
    });
    p.on("error", err => {
      // TODO: Error handling
      console.log(err);
      console.log(stderr);
      reject();
    });
    p.on("close", code => {
      console.log(`Output code ${code}`);
      console.log(stdout, stderr);
      resolve(parse(stdout));
    });
  });
};

class PytestFixtureCompletionItemProvider
  implements vscode.CompletionItemProvider {
  provideCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken,
    context: vscode.CompletionContext
  ): vscode.CompletionItem[] {
    let lineText = document.lineAt(position.line).text;
    const testPath = vscode.workspace.asRelativePath(document.fileName);
    if (shouldSuggest(lineText, position.character)) {
      if (cache[testPath]) {
        const completions = cache[testPath].map(fixture => {
          let item = new vscode.CompletionItem(
            fixture.name,
            vscode.CompletionItemKind.Variable
          );
          if (fixture.docstring) {
            item.documentation = new vscode.MarkdownString(fixture.docstring);
          }
          return item;
        });
        return completions;
      }
    }
    return [];
  }
}

const cache = {};

const cacheFixtures = document => {
  if (document.languageId == PYTHON.language) {
    const testPath = vscode.workspace.asRelativePath(document.fileName);
    const file = path.parse(testPath).base;
    console.log(`Loading fixtures for ${testPath}`);
    if (/test_/.test(file) || /conftest/.test(file)) {
      fixtureSuggestions(testPath).then(results => {
        console.log(`Found ${results.length} fixtures`);
        console.log(results);
        cache[testPath] = results;
      });
    }
  }
};

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  // TODO: Activate on load? Just currently just triggers on change.
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(editor => {
      cacheFixtures(editor.document);
    })
  );
  context.subscriptions.push(
    vscode.languages.registerCompletionItemProvider(
      PYTHON,
      new PytestFixtureCompletionItemProvider()
    )
  );
}

// this method is called when your extension is deactivated
export function deactivate() {}

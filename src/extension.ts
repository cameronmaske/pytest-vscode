"use strict";
import * as vscode from "vscode";
import cp = require("child_process");
import { parseOutput, shouldSuggest, parseCommand, isTestFile } from "./parse";

export const PYTHON: vscode.DocumentFilter = {
  language: "python",
  scheme: "file"
};

const generateRunOpts = () => {
  const pytestCommand = vscode.workspace
    .getConfiguration("pytest")
    .get("command");
  if (pytestCommand) {
    return parseCommand(pytestCommand);
  }
  // TODO: Prompt the user instead of just an error?
  vscode.window.showErrorMessage(
    "Please set `pytest.command` in your Workspace Settings, then reload to enable IntelliSense for pytest."
  );
};

const fixtureSuggestions = (filepath, cmd, args) => {
  return new Promise<any[]>((resolve, reject) => {
    args = [...args, "-q", "--fixtures"];
    if (filepath) {
      args = [...args, filepath];
    }
    let p = cp.spawn(cmd, args, {
      cwd: vscode.workspace.rootPath,
      shell: true
    });

    console.log(`Running ${cmd} : ${args} in ${vscode.workspace.rootPath}`);
    console.log(args);
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
      resolve(parseOutput(stdout));
    });
  });
};

class PytestFixtureCompletionItemProvider
  implements vscode.CompletionItemProvider {
  opts: {
    cmd: string;
    args: string[];
  };

  constructor() {
    this.opts = generateRunOpts();
  }

  provideCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken,
    context: vscode.CompletionContext
  ): vscode.CompletionItem[] {
    let lineText = document.lineAt(position.line).text;
    const testPath = vscode.workspace.asRelativePath(document.fileName);
    if (shouldSuggest(lineText, position.character)) {
      if (CACHE[testPath]) {
        const completions = CACHE[testPath].map(fixture => {
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

const CACHE = {};

const cacheFixtures = (document, opts) => {
  if (document.languageId === PYTHON.language) {
    const filePath = vscode.workspace.asRelativePath(document.fileName);
    if (isTestFile(filePath)) {
      fixtureSuggestions(filePath, opts.cmd, opts.args).then(results => {
        console.log(`Found ${results.length} fixtures for ${filePath}`);
        CACHE[filePath] = results;
      });
    }
  }
};

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  const opts = generateRunOpts();
  if (opts) {
    if (vscode.window.activeTextEditor) {
      cacheFixtures(vscode.window.activeTextEditor.document, opts);
    }
    context.subscriptions.push(
      vscode.window.onDidChangeActiveTextEditor(editor => {
        cacheFixtures(editor.document, opts);
      })
    );
  }
  context.subscriptions.push(
    vscode.languages.registerCompletionItemProvider(
      PYTHON,
      new PytestFixtureCompletionItemProvider()
    )
  );
}

// this method is called when your extension is deactivated
export function deactivate() {}

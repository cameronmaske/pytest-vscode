import path = require("path");
import { type } from "os";

export const parseOutput = (input: string) => {
  /* 
  Parse the output from `pytest --fixture` for an array of fixtures and their docstrings.
  This code is horrible, but it's a first pass.
  */
  const fixtures = [];
  let data = {};
  let docstring = "";
  for (let line of input.split("\n")) {
    const trimmedLine = line.replace(/^\s+|\s+$/g, "");
    if (trimmedLine === "") {
      if (docstring.length > 0) {
        docstring += "\n";
      }
      continue;
    }
    if (line.startsWith("    ")) {
      const trimmedLine = line.substring(4);
      if (trimmedLine.indexOf("no docstring") <= 0) {
        if (docstring.length > 0) {
          docstring += "\n";
        }
        docstring += trimmedLine;
      }
    } else if (/^\w+$/.test(line)) {
      if (data["name"]) {
        data["docstring"] = docstring.replace(/^\s+|\s+$/g, "") || null;
        fixtures.push(data);
        data = {};
        docstring = "";
      }
      data["name"] = line;
    } else if (line === "") {
      if (docstring.length > 0) {
        docstring += "\n";
      }
    } else if (line.startsWith("--") || line.startsWith("==")) {
      data["docstring"] = docstring.replace(/^\s+|\s+$/g, "") || null;
      fixtures.push(data);
      data = {};
      docstring = "";
    }
  }
  if (data["name"]) {
    data["docstring"] = docstring.replace(/^\s+|\s+$/g, "") || null;
    fixtures.push(data);
  }
  return fixtures;
};

export const parseCommand = (value: string | Array<string>) => {
  if (typeof value === "string") {
    const args = value.toString().split(" ");
    const command = args.shift();
    return {
      cmd: command,
      args: args
    };
  } else {
    const args = [...value];
    const cmd = args.shift();
    return {
      cmd: cmd,
      args: args
    };
  }
};

export const shouldSuggest = (
  lineText: string,
  cursorPosition: number
): boolean => {
  if (/def test_/.test(lineText)) {
    let lineTillCurrentPosition = lineText.substr(0, cursorPosition);
    // let lineAfterCurrentPosition = lineText.substr(
    //   cursorPosition,
    //   lineText.length
    // );
    if (
      lineTillCurrentPosition.indexOf("(") > -1 &&
      lineTillCurrentPosition.indexOf(")") === -1
    ) {
      return true;
    }
  }
  return false;
};

export const isTestFile = filePath => {
  const file = path.parse(filePath).base;
  return /test_/.test(file) || /conftest/.test(file);
};

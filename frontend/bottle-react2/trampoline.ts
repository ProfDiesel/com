import { Component } from "./react.development"

type RenderCallback = () => void

declare const validClassName: unique symbol;
type ClassName= string & { [validClassName]: true }

class BottleReact
{
  private pending_deps: Array<[Array<ClassName>, RenderCallback]> = [];

  [key: string]: InstanceType<typeof Component>;

  _check() {
    for (var i = this.pending_deps.length; --i;) {
      let [dependencies, callback] = this.pending_deps[i]
      if (dependencies.every((name: ClassName) => typeof self[name] != undefined)) {
        this.pending_deps.splice(i, 1);
        setTimeout(callback, 0);
      }
    }
  }

  _register(name: string, cls: InstanceType<typeof Component>) {
    bottlereact[name] = cls;
    this._check();
  }

  _onLoad(classes: Array<ClassName>, constructor: RenderCallback) {
    this.pending_deps.push([classes, constructor]);
    this._check();
  }
};

const bottlereact = new BottleReact()

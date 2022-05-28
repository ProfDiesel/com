from dataclasses import dataclass
import json
import random
import re
from pathlib import Path
from types import SimpleNamespace
import bottle
from bottle import Bottle
from typing import Optional, List, Any, Mapping, Final, Dict, Sequence
from itertools import chain
from pkg_resources import resource_filename

__ALL__ = ['BottleReact', '__version__']
BABEL_CORE = 'https://unpkg.com/babel-standalone@6/babel.min.js'
BOTTLEREACT_JS = 'bottlereact.js'

STATIC_ASSETS = 'static'

@dataclass
class ReactClass:
    name: str
    filename: Path

    def __call__(self, props: Optional[Mapping[str, Any]] = None, children: Optional[List['Instance']] = None):
        props = dict(props) if props else {}
        if 'key' not in props:
            props['key'] = '_br_%f' % random.random()
        return Instance(self, props, children or [])


@dataclass
class Instance:
    react_class: ReactClass
    props: Mapping[str, Any]
    children: List['Instance']

    @property
    def js_files(self) -> Sequence[Path]:
        return {self.react_class.filename: None, **chain.from_iterable(child.js_files.items() for child in self.children)}.keys()

    @property
    def react_classes(self) -> Sequence[str]:
        return {self.react_class.name: None, **chain.from_iterable(child.react_classes.items() for child in self.children)}.keys()


class BottleReact:
    def register(self, app: Bottle, asset_path: Path = 'assets'):
        @app.get('/' + STATIC_ASSETS + '/<path:path>')
        def _(path: str):
            if path == BOTTLEREACT_JS:
              return bottle.static_file(BOTTLEREACT_JS, root=resource_filename(__name__, '.'), mimetype='text/javascript')
            if path.endswith('.jsx'):
                return bottle.static_file(path, root=self.jsx_path, mimetype='text/babel')
            else:
                return bottle.static_file(path, root=asset_path)

    def __init__(self, jsx_path: Path = 'jsx'):
        self.jsx_path: Final[Path] = jsx_path
        self.dependencies: Final[Dict[Path, List[Path]]] = {}
        self.react: Final[SimpleNamespace] = SimpleNamespace()

        identifier = '[A-Za-z][_a-zA-Z0-9]*'
        class_re = re.compile('|'.join((f'(?P<class>{identifier}) = React.createClass', f'(?P<class>{identifier}) = createReactClass', f'class (?P<class>{identifier}) extends React.Component')))
        require_re = re.compile('// require (?P<requirement>.*)')
        for jsx in self.jsx_path.glob('*.jsx'):
            for line in jsx:
                if match := class_re.match(line):
                    react_class = match.group('class')
                    setattr(self.react, react_class, ReactClass(react_class, jsx))
                if match := require_re.match(line):
                    requirement = match.group('requirement')
                    self.dependencies.setdefault(jsx, []).append(requirement)


    def render_html(self, react_node: Instance, template='bottlereact', **kwargs) -> str:
        def process_path(dep):
            return bottle.htmldumps(dep if dep.startswith('http://') or dep.startswith('https://') else '/{STATIC_ASSETS}/{dep}')

        def process(dep):
            if dep.endswith('.css'):
                return f'<link href="{process_path(dep)}" rel="stylesheet">'
            elif dep.endswith('.jsx'):
                return f'<script type="text/babel" src="{process_path(dep)}"></script>'
            else:
                return f'<script src="{process_path(dep)}"></script>'

        def requirements() -> List[Path]:
            output = []

            def recurse(filename: Path):
                if filename in output:
                    return
                map(recurse, self.dependencies[filename])
                output.append(filename)
            map(recurse, react_node.js_files)

            return output

        deps_block: str = '\n'.join(process(dep for dep in (BOTTLEREACT_JS, BABEL_CORE, *requirements())))

        def dumps(s: Any) -> str:
            return json.dumps(s).replace('</', '<\\/')

        def create_node(node: Instance):
            return f'''
React.createElement(bottlereact.{node.react_class.name},
                    {dumps(node.props)},
                    [{",".join(create_node(node) if isinstance(child, Instance) else dumps(child) for child in node.children)}])'''

        init_block: str = f'''
<script>
  bottlereact._onLoad({dumps(react_node.react_classes)}, function() {{
    ReactDOM.render({create_node(react_node)}, document.getElementById('body'));
  }});
</script>'''

        return bottle.template(template, DEPS_BLOCK=deps_block, INIT_BLOCK=init_block, **kwargs)

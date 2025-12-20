import os
import shutil
import yaml
import markdown
from pathlib import Path

class SSG:
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.content_dir = self.project_dir / "content"
        self.output_dir = self.project_dir / "output"
        self.templates_dir = self.project_dir / "templates"
        self.config = self._load_config()
        self.md = markdown.Markdown(extensions=['fenced_code', 'codehilite', 'meta'])
        
    def _load_config(self):
        config_path = self.project_dir / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {"title": "My Website"}
    
    def _load_template(self, name):
        template_path = self.templates_dir / name
        if template_path.exists():
            with open(template_path, 'r') as f:
                return f.read()
        return self._default_template(name)
    
    def _default_template(self, name):
        if name == "page.html":
            return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{page_title}} - {{site_title}}</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <header>
        <h1>{{site_title}}</h1>
        <nav>{{top_nav}}</nav>
    </header>
    <main>
        {{parent_link}}
        <h2>{{page_title}}</h2>
        {{content}}
    </main>
</body>
</html>"""
        elif name == "list.html":
            return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{page_title}} - {{site_title}}</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <header>
        <h1>{{site_title}}</h1>
        <nav>{{top_nav}}</nav>
    </header>
    <main>
        {{parent_link}}
        <h2>{{page_title}}</h2>
        {{content}}
    </main>
</body>
</html>"""
        return ""
    
    def _filename_to_title(self, filename):
        name = Path(filename).stem
        name = name.replace('-', ' ').replace('_', ' ')
        return name.capitalize()
    
    def _parse_markdown(self, md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        html = self.md.convert(content)
        
        if hasattr(self.md, 'Meta') and 'title' in self.md.Meta:
            title = self.md.Meta['title'][0]
        else:
            title = self._filename_to_title(md_path.name)
        
        metadata = {
            'title': title,
            'date': self.md.Meta.get('date', [''])[0] if hasattr(self.md, 'Meta') else ''
        }
        self.md.reset()
        return html, metadata
    
    def _get_top_level_items(self):
        items = []
        for item in sorted(self.content_dir.iterdir()):
            if item.name.startswith('.'):
                continue
            if item.is_file() and item.suffix == '.md':
                items.append(('file', item))
            elif item.is_dir():
                items.append(('dir', item))
        return items
    
    def _build_top_nav(self, current_path=None):
        top_items = self._get_top_level_items()
        links = []
        
        for item_type, item in top_items:
            if item_type == 'file':
                if item.name == 'index.md':
                    title = 'Home'
                    url = '/'
                else:
                    _, meta = self._parse_markdown(item)
                    title = meta['title']
                    url = f"/{item.stem}"
            else:
                title = self._filename_to_title(item.name)
                url = f"/{item.name}"
            
            links.append(f'<a href="{url}">{title}</a>')
        
        return ' | '.join(links)
    
    def _get_relative_path(self, path):
        return path.relative_to(self.content_dir)
    
    def _get_url_path(self, rel_path):
        if rel_path == Path('.'):
            return '/'
        return '/' + str(rel_path).replace('\\', '/')
    
    def _build_parent_link(self, rel_path):
        if rel_path == Path('.') or rel_path.parent == Path('.'):
            return ''
        
        parent_url = self._get_url_path(rel_path.parent)
        return f'<p class="parent-link"><a href="{parent_url}">← Back to {rel_path.parent.name.title()}</a></p>'
    
    def _collect_directory_items(self, dir_path):
        subdirs = []
        files = []
        
        for item in dir_path.iterdir():
            if item.name.startswith('.'):
                continue
                
            if item.is_dir():
                subdirs.append(item)
            elif item.is_file() and item.suffix == '.md' and item.name != 'index.md':
                files.append(item)
        
        return sorted(subdirs), sorted(files)
    
    def _generate_list_page(self, dir_path):
        rel_path = self._get_relative_path(dir_path)
        
        if rel_path == Path('.'):
            return
        
        subdirs, files = self._collect_directory_items(dir_path)
        
        content_parts = []
        
        if subdirs:
            content_parts.append('<h3>Directories</h3><ul>')
            for subdir in subdirs:
                subdir_rel = self._get_relative_path(subdir)
                url = self._get_url_path(subdir_rel)
                content_parts.append(f'<li><a href="{url}">{subdir.name}</a></li>')
            content_parts.append('</ul>')
        
        if files:
            content_parts.append('<h3>Pages</h3><ul>')
            for file in files:
                _, meta = self._parse_markdown(file)
                file_rel = self._get_relative_path(file)
                url = self._get_url_path(file_rel.parent / file_rel.stem)
                date_str = f" ({meta['date']})" if meta['date'] else ""
                content_parts.append(f'<li><a href="{url}">{meta["title"]}</a>{date_str}</li>')
            content_parts.append('</ul>')
        
        content_html = '\n'.join(content_parts)
        
        template = self._load_template('list.html')
        html = template.replace('{{site_title}}', self.config['title'])
        html = html.replace('{{page_title}}', rel_path.name.title())
        html = html.replace('{{top_nav}}', self._build_top_nav())
        html = html.replace('{{parent_link}}', self._build_parent_link(rel_path))
        html = html.replace('{{content}}', content_html)
        
        output_path = self.output_dir / rel_path / 'index.html'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_content_page(self, md_path):
        rel_path = self._get_relative_path(md_path)
        content_html, metadata = self._parse_markdown(md_path)
        
        if md_path.name == 'index.md' and rel_path.parent == Path('.'):
            output_path = self.output_dir / 'index.html'
            parent_link = ''
        else:
            stem = md_path.stem
            output_path = self.output_dir / rel_path.parent / stem / 'index.html'
            
            if rel_path.parent == Path('.'):
                parent_link = ''
            else:
                parent_link = self._build_parent_link(rel_path.parent)
        
        template = self._load_template('page.html')
        html = template.replace('{{site_title}}', self.config['title'])
        html = html.replace('{{page_title}}', metadata['title'])
        html = html.replace('{{top_nav}}', self._build_top_nav())
        html = html.replace('{{parent_link}}', parent_link)
        html = html.replace('{{content}}', content_html)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _copy_static_files(self):
        css_src = self.templates_dir / 'style.css'
        if css_src.exists():
            shutil.copy(css_src, self.output_dir / 'style.css')
        
        error_src = self.templates_dir / '404.html'
        if error_src.exists():
            shutil.copy(error_src, self.output_dir / '404.html')
    
    def _process_directory(self, dir_path):
        self._generate_list_page(dir_path)
        
        for item in dir_path.iterdir():
            if item.name.startswith('.'):
                continue
            
            if item.is_file() and item.suffix == '.md':
                self._generate_content_page(item)
            elif item.is_dir():
                self._process_directory(item)
    
    def build(self):
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self._process_directory(self.content_dir)
        
        self._copy_static_files()
        
        print(f"Site built successfully in {self.output_dir}")


def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python ssg.py <project_directory>")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    
    if not os.path.isdir(project_dir):
        print(f"Error: {project_dir} is not a valid directory")
        sys.exit(1)
    
    ssg = SSG(project_dir)
    ssg.build()


if __name__ == "__main__":
    main()
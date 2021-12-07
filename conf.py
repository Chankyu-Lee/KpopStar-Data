# Sphinx 문서 작성기를 위한 구성 파일입니다.
#
# 이 파일에는 가장 일반적인 옵션만 포함되어 있습니다. 
# 목록은 문서를 참조하십시오:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# --경로 설정--------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# 디렉토리가 상대적인 경우 이 디렉토리를 sys.path에 추가하세요.
# 문서 루트, 여기에 표시된 것처럼 os.path.abspath를 사용하여 절대적으로 만듭니다.

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))


# 프로젝트 정보

project = 'Blackpink Data'
copyright = '2021, Marco Fantauzzo'
author = 'Marco Fantauzzo'

# alpha/beta/rc 태그를 포함한 정식 버전
release = '1.0.0'


# 일반 구성

import sphinx_rtd_theme

# 여기에 모든 Sphinx 확장 모듈 이름을 문자열로 추가합니다. 
# Sphinx와 함께 제공되는 확장('sphinx.ext.*') 
# 또는 사용자 지정 확장일 수 있습니다.
extensions = [
    'sphinx.ext.autodoc',
    "sphinx_rtd_theme"
    ]

# 이 디렉토리와 관련하여 여기에 템플릿이 포함된 모든 경로를 추가합니다.
templates_path = ['_templates']

# 소스 파일을 찾을 때 무시할 파일 및 디렉토리와 일치하는 소스 디렉토리에 상대적인 패턴 목록입니다.
# 이 패턴은 html_static_path 및 html_extra_path에도 영향을 줍니다.
exclude_patterns = []


# HTML 출력 옵션

# HTML 및 HTML 도움말 페이지에 사용할 테마입니다. 기본 제공 테마 목록은 설명서를 참조하세요.
html_theme = "sphinx_rtd_theme"

html_theme_options = {
    'display_version': False,
    'style_nav_header_background': '#cc5c79'
}

# 이 디렉토리에 상대적인 사용자 정의 정적 파일(예: 스타일 시트)을 포함하는 모든 경로를 여기에 추가하십시오. 
# 내장 정적 파일 다음에 복사되므로 "default.css"라는 파일이 내장 "default.css"를 덮어씁니다.
html_static_path = ['_static']
html_theme_path = ["_themes", ]
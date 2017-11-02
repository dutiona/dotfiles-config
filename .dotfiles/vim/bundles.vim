
" Load bundles (with Vundle)
call plug#begin('~/.dotfiles/vim/plugged')

" Auto close pair of characters like (, [, {,… 
" (can be deactivated with <Leader>a
Plug 'jiangmiao/auto-pairs'

" EasyMotion provides a much simpler way to use some motions in vim.
" (activated with <Leader><Leader>
"
" Commands:
"   * <Leader><Leader>w
"   * <Leader><Leader>b
Plug 'Lokaltog/vim-easymotion'

" The ultimate vim statusline utility.
" Plug 'Lokaltog/vim-powerline'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

" Align extension
" :Tabularize /pattern
"
" Examples :
"   * :Tabularize / \+\zs (align fstab entries)
Plug 'godlygeek/tabular'

" File explorer
" mapped to <F8>
Plug 'scrooloose/nerdtree', { 'on': 'NERDTreeTabsToggle' }
Plug 'jistr/vim-nerdtree-tabs'

" Check the syntax of the current file
Plug 'scrooloose/syntastic'

" File-type sensible comments
" mapped to <F2>
"
" Support new FileType :
" autocmd FileType apache set commentstring=#\ %s
Plug 'tpope/vim-commentary'

" Plug 'scrooloose/nerdcommenter'
" Plug 'tomtom/tcomment_vim'

" Git wrapper
"
" Commands:
"   * :Gstatus, '-' toggle the status of an entry (add/reset) then 'C' for commit
"   * :Gcommit
"   * :Glog :Ggrep :Gedit to navigate into the repository
"       (blob, tree, commit, or tag)
Plug 'tpope/vim-fugitive'

" File type plugin to help edit XML documents.
Plug 'sukima/xmledit'

" Surround with something
"
" Commands:
"   * in visual mode, <Leader>s then a character like '"`{([<
"   * hs"' change the " surrounding to '
"   * ds" delete the " surrounding
Plug 'surround.vim'

Plug 'gnupg.vim'
Plug 'matchit.zip'

" Themes
Plug 'wombat256.vim'
Plug 'junegunn/seoul256.vim'
Plug 'nanotech/jellybeans.vim'
Plug 'romainl/Apprentice'
" Plug 'morhetz/gruvbox'

if executable('ctags')
    Plug 'Tagbar'
endif

" Interactive command execution (used by other plugins)
" This plugin need to be built: (cd ~/.vim/bundle/vimcore.vim; make)
Plug 'Shougo/vimproc.vim', { 'do': 'make' }

" Unite and create user interfaces
"
" <Leader>p : Search file
" <Leader>/ : Grep files
" <Leader>b : Switch buffer
Plug 'Shougo/unite.vim'

" Outline (should repalec Tagbar)
"
" :Unite outline
Plug 'Shougo/unite-outline'

" Powerfull shell implemented by vim
Plug 'Shougo/vimshell.vim'

" Powerfull file explorer
Plug 'Shougo/vimfiler.vim'

" Neo-completion with cache
if has('lua') && (v:version > 703 || (v:version == 703 && has('patch885')))
    Plug 'Shougo/neocomplete.vim'
else
    Plug 'Shougo/neocomplcache.vim'
endif

" Neo-snippet
Plug 'Shougo/neosnippet'
Plug 'Shougo/neosnippet-snippets'

" Incsearch
"
" Improved incremental searching for Vim
Plug 'haya14busa/incsearch.vim'


" Expand visual selection
"
" +/_ increase/decrease the selection
Plug 'terryma/vim-expand-region'

" Quick fixsigns (pan on the left with signs)
Plug 'tomtom/quickfixsigns_vim'

" Unicode character metadata
"
" ga on a character reveals its representation in decimal, octal, and hex
Plug 'tpope/vim-characterize'

" Better json support
Plug 'elzr/vim-json'

" Rainbow parentheses improved
Plug 'luochen1990/rainbow'

" Register preview
Plug 'junegunn/vim-peekaboo'

" Tmux integration
Plug 'tpope/vim-tbone'

" More syntax highlighting filetypes
Plug 'sheerun/vim-polyglot'

" Write html/xml
Plug 'rstacruz/sparkup', { 'rtp': 'vim/' }

" Not tested, TODO
" Plug 'Clam'
" Plug 'unimpaired.vim'


call plug#end()

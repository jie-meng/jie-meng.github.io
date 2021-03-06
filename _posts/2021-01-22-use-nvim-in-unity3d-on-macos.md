---
title: Use nvim in Unity3d on MacOS
layout: post
date: 2021-01-22 16:31:00 +0800

categories: unity3d
---

## Compile omnisharp-roslyn server

Clone [omnisharp-roslyn](https://github.com/OmniSharp/omnisharp-roslyn)

Use command `./build.sh` to compile omnisharp-roslyn server (omnisharp-roslyn will be compiled with local environment mono)

## nvim settings

Create `~/.config/nvim/omnisharp.config.vim`

Copy the following script to omnisharp.config.vim.

Don't forget to change the value of `let g:OmniSharp_server_path = ''` to the absolute path of OmniSharp.exe which built just now.

{% highlight vimscript %}

" OmniSharp
"" Compile omnisharp-roslyn locally and set the artifacts OmniSharp.exe to OmniSharp_server_path
"" https://github.com/OmniSharp/omnisharp-roslyn
let g:OmniSharp_server_path = '/Users/{username}/{directory}/omnisharp-roslyn/artifacts/publish/OmniSharp.Stdio.Driver/mono/OmniSharp.exe'

"" The roslyn server releases come with an embedded Mono, but this can be overridden to use the installed Mono by setting g:OmniSharp_server_use_mono
let g:OmniSharp_server_use_mono = 1

"" Timeout in seconds to wait for a response from the server
let g:OmniSharp_timeout = 1

"" Get Code Issues and syntax errors
let g:syntastic_cs_checkers = ['syntax', 'semantic', 'issues']

augroup omnisharp_commands
    autocmd!

    "" Set autocomplete function to OmniSharp (if not using YouCompleteMe completion plugin)
    autocmd FileType cs setlocal omnifunc=OmniSharp#Complete

    "" automatic syntax check on events (TextChanged requires Vim 7.4)
    autocmd BufEnter,TextChanged,InsertLeave *.cs SyntasticCheck

    "" The following commands are contextual, based on the current cursor position.
    autocmd FileType cs nnoremap gd :OmniSharpGotoDefinition<cr>
    autocmd FileType cs nnoremap <space>fi :OmniSharpFindImplementations<cr>
    autocmd FileType cs nnoremap <space>ft :OmniSharpFindType<cr>
    autocmd FileType cs nnoremap <space>fs :OmniSharpFindSymbol<cr>
    autocmd FileType cs nnoremap <space>fu :OmniSharpFindUsages<cr>
    "" finds members in the current buffer
    autocmd FileType cs nnoremap <space>fm :OmniSharpFindMembers<cr>
    "" cursor can be anywhere on the line containing an issue
    autocmd FileType cs nnoremap <space>fx :OmniSharpFixUsings<cr>
    autocmd FileType cs nnoremap <space>tt :OmniSharpTypeLookup<cr>
    autocmd FileType cs nnoremap <space>dc :OmniSharpDocumentation<cr>
    "" navigate up by method/property/field
    autocmd FileType cs nnoremap <C-K> :OmniSharpNavigateUp<cr>
    "" navigate down by method/property/field
    autocmd FileType cs nnoremap <C-J> :OmniSharpNavigateDown<cr>
    "" Contextual code actions (requires CtrlP or unite.vim)
    autocmd FileType cs nnoremap <space>a :OmniSharpGetCodeActions<cr>
    "" Run code actions with text selected in visual mode to extract method
    autocmd FileType cs vnoremap <space>a :call OmniSharp#GetCodeActions('visual')<cr>
    "" rename with dialog
    autocmd FileType cs nnoremap <space>rm :OmniSharpRename<cr>
    "" Force OmniSharp to reload the solution. Useful when switching branches etc.
    autocmd FileType cs nnoremap <space>cf :OmniSharpCodeFormat<cr>
    "" (Experimental - uses vim-dispatch or vimproc plugin) - Restart the omnisharp server for the current solution
    autocmd FileType cs nnoremap <space>rs :OmniSharpRestartServer<cr>
    "" Add syntax highlighting for types and interfaces
    autocmd FileType cs nnoremap <space>th :OmniSharpHighlightTypes<cr>
augroup END

{% endhighlight %}

Add following lines to `~/.config/nvim/init.vim`.

{% highlight vimscript %}

Plug 'OmniSharp/omnisharp-vim'

source ~/.config/nvim/omnisharp.config.vim

{% endhighlight %}

Run `nvim`, execute `:PlugInstall` to install omnisharp-vim plugin.

## Unity3D development in nvim

- Run nvim from the directory _{project_dir}/Assets/Scripts/_.

- Create/Delete/Rename/Move C# script files from Unity3D Editor (Which will handle the .meta files).

- After operation of script files in Unity3D, Go to Preferences -> External Tools and Click __Regenerate project files__ to update the sln and csproj file.

- Use `<space>rs` in nvim to restart omnisharp server, which will reload sln and csproj files.


## Reference

[omnisharp-roslyn](https://github.com/OmniSharp/omnisharp-roslyn)

[omnisharp-vim](https://libraries.io/github/OmniSharp/omnisharp-vim)

[Unity3D and .NET Framework](https://github.com/OmniSharp/omnisharp-vim/wiki/Unity3D-and-.NET-Framework)

[Unity3D Command line arguments](https://docs.unity3d.com/Manual/CommandLineArguments.html)

[Issue: Doesn't download OmniSharp-Roslyn before trying to start on macOS](https://github.com/OmniSharp/omnisharp-vim/issues/506)

[coc-omnisharp](https://github.com/coc-extensions/coc-omnisharp)

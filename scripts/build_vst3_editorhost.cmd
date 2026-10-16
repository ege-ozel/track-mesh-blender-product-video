@echo off
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
if errorlevel 1 exit /b 1
"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" -S "D:\CodeSpace\track-mesh\plugins\vst3" -B "%~dp0..\tools\vst3-editorhost" -G Ninja -DCMAKE_BUILD_TYPE=Release -DTRACKMESH_BUILD_EDITOR_HOST=ON -DTRACKMESH_AGENT="D:\CodeSpace\track-mesh\.build\vst3\VST3\Release\TrackMesh.vst3\Contents\x86_64-win\trackmesh-agent.exe" -DTRACKMESH_DESKTOP="D:\CodeSpace\track-mesh\.build\vst3\VST3\Release\TrackMesh.vst3\Contents\x86_64-win\trackmesh-desktop.exe"
if errorlevel 1 exit /b 1
"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe" --build "%~dp0..\tools\vst3-editorhost" --target editorhost --parallel 4
exit /b %errorlevel%

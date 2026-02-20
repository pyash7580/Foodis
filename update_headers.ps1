$basePath = "d:\Foodis\frontend\src\pages"
Get-ChildItem -Path $basePath -Filter *.js -Recurse | ForEach-Object {
    $role = ""
    if ($_.FullName -like "*\pages\client\*") { $role = "CLIENT" }
    elseif ($_.FullName -like "*\pages\rider\*") { $role = "RIDER" }
    elseif ($_.FullName -like "*\pages\restaurant\*") { $role = "RESTAURANT" }
    elseif ($_.FullName -like "*\pages\admin\*") { $role = "ADMIN" }

    if ($role) {
        $content = Get-Content $_.FullName -Raw
        # Search for Authorization: `Bearer ${token}`
        if ($content -like "*Authorization: ``Bearer `${token}``*") {
            if ($content -notlike "*'X-Role': '$role'*") {
                $old = "Authorization: ``Bearer `${token}``"
                $new = "Authorization: ``Bearer `${token}``, 'X-Role': '$role'"
                $newContent = $content.Replace($old, $new)
                $newContent | Set-Content $_.FullName
                Write-Host "Updated $($_.Name) with role $role"
            }
        }
    }
}

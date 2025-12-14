# Troubleshooting

:::{index} Troubleshooting
:::

This guide covers common issues and their solutions.

## Network and Download Errors

### webCache:retrievalError

**Symptom**: Error message indicating Arelle couldn't download a file from a URL.

**Causes and Solutions**:

1. **Missing taxonomy package** (most common)
   - Install the appropriate [taxonomy package][taxonomy-packages] for your jurisdiction
   - Example: SEC filings need US GAAP packages, ESEF filings need ESEF packages

2. **Network connectivity issues**
   - Check your internet connection
   - Verify proxy settings: `arelleCmdLine --proxy=show`
   - Configure proxy: `arelleCmdLine --proxy=http://proxy.example.com:8080`

3. **Firewall blocking requests**
   - Corporate firewalls may block Arelle's HTTP requests
   - Work with IT to whitelist taxonomy server domains
   - Or use offline mode with packages: `--internetConnectivity=offline --packages=...`

4. **Server temporarily unavailable**
   - Taxonomy servers may experience downtime
   - Try again later or use local packages

5. **SSL/Certificate errors**
   - Try `--noCertificateCheck` (use with caution)
   - Update your system's certificate store

### xbrl:schemaImportMissing

**Symptom**: Schema import failed, referenced schema not found.

**Solution**: Usually the same as `webCache:retrievalError` - install the appropriate taxonomy package.

## GUI Issues

### Arelle Won't Start

**Windows**:
1. Run the uninstaller if available: `C:\Program Files\Arelle\Uninstall.exe`
2. Delete the application directory: `C:\Program Files\Arelle`
3. Delete the configuration directory: `%LOCALAPPDATA%\Arelle`
4. Reinstall from the [latest release][install]

**macOS**:
1. Delete the application: `/Applications/Arelle.app`
2. Delete configuration: `~/Library/Application Support/Arelle`
3. Delete cache: `~/Library/Caches/Arelle`
4. Reinstall from the [latest release][install]

**Linux**:
1. Delete the extracted Arelle directory
2. Delete configuration: `~/.config/arelle/`
3. Reinstall from the [latest release][install]

### GUI Crashes on Startup

- Often caused by corrupted configuration files
- Delete the configuration directory (see above) and restart
- If the issue persists after clean install, [report a bug][bug-report]

### Locale/Character Encoding Issues

- Common on systems with non-English locales
- Try setting the UI language explicitly: `--uiLang=en`
- On macOS Big Sur+, ensure you're using a compatible Arelle version

## Plugin Issues

### Plugin Not Loading

**Symptoms**: Plugin doesn't appear or functions don't work.

**Solutions**:

1. **Verify plugin path**:
   ```bash
   # By name (must be in plugin directory)
   arelleCmdLine --plugins=myPlugin --file report.xbrl --validate

   # By path (absolute or relative)
   arelleCmdLine --plugins=/path/to/myPlugin --file report.xbrl --validate
   ```

2. **Check for errors in output**: Run with `--logLevel=debug` to see plugin loading details

3. **Multiple plugins**: Separate with `|`:
   ```bash
   arelleCmdLine --plugins="plugin1|plugin2" --file report.xbrl --validate
   ```

### Plugin Conflicts

**Symptom**: Unexpected behavior when multiple plugins are loaded.

**Solutions**:
- Load only the plugins you need for each task
- Check plugin documentation for known incompatibilities
- Try loading plugins individually to identify the conflict

### Plugins "Disappearing" in GUI

**Symptom**: Previously enabled plugins no longer appear.

**Cause**: Plugin configuration is stored separately from the application.

**Solutions**:
1. Re-enable plugins via `Help` > `Manage plug-ins`
2. After clean install, plugin selections must be reconfigured
3. CLI plugin selections (`--plugins`) don't persist to GUI

## Validation Issues

### Unexpected Validation Errors

1. **Wrong disclosure system**: Ensure you're using the correct one for your jurisdiction
   ```bash
   arelleCmdLine --disclosureSystem=help  # List available systems
   ```

2. **Wrong taxonomy year**: Use packages matching your report's taxonomy year

3. **Strict vs pragmatic mode**: Try pragmatic mode first for SEC filings:
   ```bash
   arelleCmdLine --disclosureSystem=efm-pragmatic --file report.xbrl --validate
   ```

### Validation Takes Too Long

1. **Skip base taxonomy validation** for known-good taxonomies:
   ```bash
   arelleCmdLine --baseTaxonomyValidation=none --file report.xbrl --validate
   ```

2. **Use local packages** instead of downloading:
   ```bash
   arelleCmdLine --packages=/path/to/packages/ --internetConnectivity=offline --file report.xbrl --validate
   ```

3. **Disable formula processing** if not needed:
   ```bash
   arelleCmdLine --formula=none --file report.xbrl --validate
   ```

## Output Issues

### Missing or Empty Output Files

1. **Check file extension**: Output format is determined by extension
   - `.csv`, `.json`, `.html`, `.xml` for different formats

2. **Verify the data exists**: Some views may be empty if the report doesn't contain that data

3. **Check for validation errors**: Errors during loading may prevent output generation

### Viewer Missing Concept Details

**Symptom**: iXBRL viewer or Edgar Renderer shows facts but not concept labels/documentation.

**Cause**: Taxonomy files couldn't be loaded.

**Solution**: Install the appropriate [taxonomy package][taxonomy-packages] and regenerate the viewer.

## Getting More Information

### Enable Debug Logging

```bash
arelleCmdLine --logLevel=debug --logFile=debug.log --file report.xbrl --validate
```

### Run Diagnostics

```bash
arelleCmdLine --diagnostics
```

This outputs system information useful for bug reports.

### Check Version

```bash
arelleCmdLine --version
arelleCmdLine --about
```

Ensure you're running a recent version before reporting issues.

## Reporting Bugs

If none of the above solutions work:

1. Run `arelleCmdLine --diagnostics` and include the output
2. Include the exact command you're running
3. Include relevant log output (use `--logLevel=debug` if needed)
4. If possible, include a minimal test case that reproduces the issue
5. [Open an issue][bug-report] on GitHub

[taxonomy-packages]: project:user_guides/taxonomy_packages.md
[install]: project:install.md
[bug-report]: project:index.md#bug-report-or-feature-request

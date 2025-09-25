Frequently Asked Questions
==========================

General Questions
-----------------

**Q: Why not just store binaries in the source repository?**

A: Storing binaries in source repositories bloats repo size, slows cloning, and lacks proper
expiry mechanisms. |grb| gives you the best of both worlds: separation with
traceability.

**Q: Does this require a special Git server?**

A: No! It works with any standard Git server including GitHub, GitLab, Bitbucket, or self-hosted options.

**Q: How does this compare to Git LFS?**

A: |grb| complements Git LFS rather than replacing it. While Git LFS handles large
files in your source repository, |grb| manages build artifacts separately with
expiry policies and build avoidance features.

**Q: Is git-recycle-bin production-ready?**

A: |grb| is actively developed and used in various projects. However, as with any
tool, evaluate it thoroughly in your specific environment before production deployment.

**Q: What license is git-recycle-bin released under?**

A: |grb| is open source. Check the LICENSE file in the repository for specific licensing terms.

Technical Questions
-------------------

**Q: How large can artifacts be?**

A: |grb| works with the same size constraints as Git itself. Very large binaries
(>100MB) might be better served by Git LFS integration (planned for future releases).

**Q: Does this work with CI/CD pipelines?**

A: Yes! It's especially valuable in CI/CD contexts where build avoidance can significantly
reduce pipeline times. The tool integrates naturally with shell scripts and automation.

**Q: Can I use this with monorepos?**

A: Absolutely. You can organize artifacts by path to maintain clean separation for different projects within a monorepo.

**Q: How does garbage collection work?**

A: Artifacts with expired dates are automatically cleaned up when you run ``git gc`` in the
artifact repository. The expiry dates are encoded in the branch names, making cleanup efficient.

**Q: Can I query artifacts without downloading them?**

A: Yes! |grb| uses metadata-only refs that allow you to query artifact
information without downloading the full binary trees.

**Q: How does build avoidance work technically?**

A: |grb| uses Git notes to inform your source repository about available
artifacts. Your build scripts can check for notes on the current commit and download
matching artifacts instead of rebuilding.

**Q: What metadata is stored with artifacts?**

A: Artifacts include comprehensive metadata such as:

* Source repository and commit SHA
* Branch information and Git status at build time
* MIME type and location information
* Configurable expiry dates
* Custom metadata fields

**Q: Can I use custom expiry policies?**

A: Yes, you can set custom expiry dates using natural language like "in 1 month",
"next Friday", or specific dates. The tool uses flexible date parsing.

**Q: Does this work with Git submodules?**

A: |grb| can work with repositories that use submodules, but each repository is
handled independently. Artifacts are linked to the specific repository's commits.

Usage and Workflow Questions
-----------------------------

**Q: How do I integrate this into my existing build process?**

A: Add artifact push/pull steps to your build scripts. Check the
:doc:`examples/basic-workflow` documentation for common integration patterns.

**Q: Can multiple developers share the same artifact repository?**

A: Yes, that's one of the main use cases. Multiple developers and CI systems can push to
and pull from the same artifact repository with proper Git authentication.

**Q: What happens if I push an artifact with the same name multiple times?**

A: New artifacts create new branches with timestamps. The "latest" tag always points to the
most recent artifact, while older versions remain available until they expire.

**Q: How do I handle artifacts that shouldn't expire?**

A: You can set very long expiry dates (e.g., "in 10 years") or use a separate workflow
for permanent artifacts. Future versions may include permanent artifact support.

**Q: Can I search for artifacts by metadata?**

A: Currently, you can list and filter artifacts by path and name. More advanced metadata
search capabilities are planned for future releases.

Troubleshooting
---------------

**Q: What if my artifact fails to push?**

A: Common causes and solutions:

* **Permission denied**: Ensure you have write access to the artifact repository
* **Remote not found**: Verify the remote URL is correct and accessible
* **Large files**: Check if your Git server has size limits
* **Network issues**: Use ``--verbose`` flag to see detailed error messages

**Q: How do I debug missing artifacts?**

A: Use the ``list`` command to see all available artifacts:

.. code-block:: bash

   git_recycle_bin.py list <remote> --name "Your-Artifact-Name"

Check that branch names and paths match exactly what you're expecting.

**Q: Why can't I download an artifact?**

A: Potential issues:

* **Artifact expired**: Check if the artifact's expiry date has passed
* **Wrong path**: Verify you're specifying the correct download path
* **Permissions**: Ensure you have read access to the artifact repository
* **Network connectivity**: Test basic Git operations to the remote

**Q: The tool is running slowly. How can I optimize performance?**

A: Performance tips:

* Use ``--rm-tmp`` flag to clean up temporary repositories
* Consider using local artifact repositories for development
* Use metadata-only queries when you don't need the full artifacts
* Ensure your Git server has good network connectivity

**Q: How do I recover from a corrupted artifact repository?**

A: |grb| uses standard Git operations, so standard Git recovery techniques apply:

* Use ``git fsck`` to check repository integrity
* Restore from backups if available
* Recreate artifacts from source if necessary

**Q: Can I migrate artifacts between repositories?**

A: Yes, but this requires manual steps:

1. Clone the source artifact repository
2. Push to the new artifact repository
3. Update your build scripts to use the new remote

Future versions may include migration tools.

**Q: How do I handle authentication issues?**

A: |grb| uses standard Git authentication:

* **SSH keys**: Ensure your SSH keys are properly configured
* **HTTPS**: Use Git credential helpers for token-based authentication
* **Corporate networks**: Configure Git to work with proxies if needed

See your Git server's documentation for specific authentication setup.

Getting Help
------------

If you encounter issues not covered in this FAQ:

1. **Check the logs**: Use the ``--verbose`` flag for detailed output
2. **Search existing issues**: Check the `GitHub Issues <https://github.com/ArtifactLabs/git-recycle-bin/issues>`_ page
3. **Create a minimal reproduction**: Prepare a simple example that demonstrates the issue
4. **Open a new issue**: Include your environment details, error messages, and reproduction steps

When reporting issues, please include:

* Operating system and version
* Git version (``git --version``)
* Python version (``python --version``)
* |grb| version (``git_recycle_bin.py --version``)
* Complete error messages and stack traces
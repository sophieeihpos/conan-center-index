import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools


class Krb5Conan(ConanFile):
  name = 'krb5'
  description = 'MIT Kerberos, a network authentication protocol.'
  license = 'MIT'
  url = 'https://web.mit.edu/kerberos/'
  settings = 'os', 'compiler', 'build_type', 'arch'
  options = {'shared': [True, False]}
  default_options = 'shared=True'
  generators = 'cmake', 'cmake_find_package'

  @property
  def _source_subfolder(self):
    return 'source_subfolder'

  def source(self):
    conan_data = self.conan_data['sources'][self.version]
    tools.get(url=conan_data['url'], sha256=conan_data['sha256'])
    extracted_dir = self.name + '-' + self.version
    os.rename(extracted_dir, self._source_subfolder)

  def build_requirements(self):
    self.build_requires('bison/3.7.1')

  def build(self):
    conf_args = []
    autotools = AutoToolsBuildEnvironment(self)
    if self.options.shared:
      conf_args.extend(['--enable-shared', '--disable-static'])
    else:
      conf_args.extend(['--disable-shared', '--enable-static'])
    conf_args.append('--without-system-db')

    # -fno-common is default in gcc10
    autotools.flags.append('-fcommon')
    autotools.configure(
        configure_dir=os.path.join(
            self._source_subfolder,
            'src'),
        args=conf_args)
    autotools.make()

  def package(self):
    autotools = AutoToolsBuildEnvironment(self)
    autotools.install()

  def package_info(self):

    self.cpp_info.names["cmake_find_package"] = "krb5"
    self.cpp_info.names["cmake_find_package_multi"] = "krb5"
    libs = [
        'libkrb5support',
        'libk5crypto',
        'libcom_err',
        'libkrb5',
        'libgssapi_krb5',
        'libgssrpc',
        'libkadm5clnt',
        'libkadm5srv',
        'libkdb5',
        'libkrad']

    for target in libs:
      libname = target.split('lib')[1]
      self.cpp_info.components[target].libs = [libname]
      self.cpp_info.components[target].names['cmake_find_package'] = libname
      self.cpp_info.components[target].names['cmake_find_package_multi'] = libname
      self.cpp_info.components[target].names['pkg_config'] = libname

    self.cpp_info.components['libkrb5support'].system_libs = [
        'dl', 'keyutils', 'resolv']
    self.cpp_info.components['libcom_err'].requires = ['libkrb5support']
    self.cpp_info.components['libk5crypto'].requires = ['libkrb5support']
    self.cpp_info.components['libkrb5'].requires = [
        'libcom_err', 'libk5crypto']
    self.cpp_info.components['libgssapi_krb5'].requires = ['libkrb5']
    self.cpp_info.components['libgssrpc'].requires = ['libgssapi_krb5']
    self.cpp_info.components['libkadm5clnt'].requires = ['libgssrpc']
    self.cpp_info.components['libkadm5srv'].requires = ['libgssrpc']
    self.cpp_info.components['libkdb5'].requires = ['libgssrpc']
    self.cpp_info.components['libkrad'].requires = ['libkrb5']

    # dependency tree

    # libkadm5clnt:
    #   -> libgssrpc:
    #     -> libgssapi_krb5:
    #       -> libkrb5:
    #         -> libcom_err:
    #           -> libkrb5support:
    #             -> dl
    #             -> keyutils
    #             -> resolv
    #         -> libk5crypto:
    #           -> libkrb5support:
    #             -> dl
    #             -> keyutils
    #             -> resolv

    # libkadm5srv:
    #   -> libgssrpc:
    #     -> libgssapi_krb5:
    #       -> libkrb5:
    #         -> libcom_err:
    #           -> libkrb5support:
    #             -> dl
    #             -> keyutils
    #             -> resolv
    #         -> libk5crypto:
    #           -> libkrb5support:
    #             -> dl
    #             -> keyutils
    #             -> resolv

    # libkdb5:
    #   -> libgssrpc:
    #     -> libgssapi_krb5:
    #       -> libkrb5:
    #         -> libcom_err:
    #           -> libkrb5support:
    #             -> dl
    #             -> keyutils
    #             -> resolv
    #         -> libk5crypto:
    #           -> libkrb5support:
    #             -> dl
    #             -> keyutils
    #             -> resolv

    # libkrad:
    #   -> libkrb5:
    #     -> libcom_err:
    #       -> libkrb5support:
    #         -> dl
    #         -> keyutils
    #         -> resolv
    #     -> libk5crypto:
    #       -> libkrb5support:
    #         -> dl
    #         -> keyutils
    #         -> resolv

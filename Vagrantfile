Vagrant.configure("2") do |config|
    config.vm.synced_folder ".", "/home/vagrant/coldfront-plugin-openstack/"
    config.vm.network :private_network

    config.vm.define "openstack" do |openstack|
        openstack.vm.box = "generic/ubuntu2004"

        openstack.vm.provider "vmware_fusion" do |vb|
            vb.gui = false
            vb.memory = "9000"
            vb.cpus = "4"
        end

        openstack.vm.provision "shell", privileged: false, inline: <<-SHELL
            set -xe

            cd ~/coldfront-plugin-openstack
            ./ci/devstack.sh
            ./ci/setup.sh
            ./ci/run_functional_tests.sh
        SHELL
    end

    config.vm.define "openshift" do |openshift|
        openshift.vm.box = "generic/fedora35"

        openshift.vm.provider "vmware_fusion" do |vb|
            vb.gui = false
            vb.memory = "4096"
            vb.cpus = "4"
        end

        openshift.vm.provision "shell", privileged: false, inline: <<-SHELL
            set -xe

            sudo dnf module enable -y cri-o:1.21
            sudo dnf install -y cri-o cri-tools
            sudo dnf install -y python3-devel python3-virtualenv

            sudo systemctl enable crio --now

            sudo dnf install -y podman firewalld
            sudo curl -o /etc/systemd/system/microshift.service \
                 https://raw.githubusercontent.com/redhat-et/microshift/main/packaging/systemd/microshift-containerized.service
            sudo systemctl enable firewalld --now
            sudo firewall-cmd --zone=trusted --add-source=10.42.0.0/16 --permanent
            sudo firewall-cmd --zone=public --add-port=80/tcp --permanent
            sudo firewall-cmd --zone=public --add-port=443/tcp --permanent
            sudo firewall-cmd --zone=public --add-port=5353/udp --permanent
            sudo firewall-cmd --reload
            sudo systemctl enable microshift --now

            curl -O https://mirror.openshift.com/pub/openshift-v4/$(uname -m)/clients/ocp/stable/openshift-client-linux.tar.gz
            sudo tar -xf openshift-client-linux.tar.gz -C /usr/local/bin oc kubectl

            mkdir ~/.kube
            sudo podman cp microshift:/var/lib/microshift/resources/kubeadmin/kubeconfig ~/.kube/config
            sudo chown `whoami`: ~/.kube/config

            echo '127.0.0.1  onboarding-onboarding.cluster.local' | sudo tee -a /etc/hosts

            # For some reason it complains about no matches for kind "ImageStream"
            # Try waiting for things to settle.
            sleep 60

            git clone https://github.com/CCI-MOC/openshift-acct-mgt
            # TODO: Get the deployment change upstream
            cp coldfront-plugin-openstack/ci/acct-mgt-deployment.yaml openshift-acct-mgt/k8s/base/deployment.yaml
            cd openshift-acct-mgt
            oc apply -k k8s/overlays/crc
            oc wait -n onboarding --for=condition=available --timeout=800s deployment/onboarding

            sleep 10

            curl -u admin:pass https://onboarding-onboarding.cluster.local/users/test -k
        SHELL
    end
end

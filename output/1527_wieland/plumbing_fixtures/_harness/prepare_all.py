"""Publish all currently supported source-specific native family inputs."""
import prepare_products as p
import prepare_hansgrohe
import prepare_brizo
import prepare_completion_a
import prepare_completion_b
import prepare_completion_c
import prepare_completion_d

if __name__=='__main__':
    p.prepare_hansgrohe_pilot()
    p.prepare_brizo_pilot()
    prepare_hansgrohe.prepare()
    prepare_brizo.prepare()
    prepare_completion_a.prepare()
    prepare_completion_b.prepare()
    prepare_completion_c.prepare()
    prepare_completion_d.prepare()
    p.publish()

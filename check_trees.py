from home.models import TreeSubmission

trees = TreeSubmission.objects.all()
print(f'Total trees: {trees.count()}')
print('Status breakdown:')
for status in ['pending', 'approved', 'rejected']:
    count = TreeSubmission.objects.filter(status=status).count()
    print(f'  {status}: {count}')

print('\nApproved trees:')
for tree in TreeSubmission.objects.filter(status='approved'):
    print(f'  - {tree.species} at ({tree.latitude}, {tree.longitude})')

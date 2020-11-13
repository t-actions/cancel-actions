# Cancel Previous Actions

Github Actions to cancel previous actions that is triggered by same info but not completed
> All uncompleted actions are listed from https://docs.github.com/en/free-pro-team@latest/rest/reference/actions#list-workflow-runs-for-a-repository

## Usage

```yaml
- uses: t-actions/cancel-actions@master
  with:
    # Github token for related repository
    # Default: ${{ github.token }}
    token: ''

    # branch parameter of listing API
    # Default: ${{ github.ref }}
    ref: ''

    # event parameter of listing API 
    # Default: ${{ github.event_name }}
    event_name: ''

    # Ingore error if it is not empty
    # Default is empty
    ignore_error: ''
```
